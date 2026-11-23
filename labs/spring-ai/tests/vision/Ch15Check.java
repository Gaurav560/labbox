package com.atlas.check;

import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.Base64;

import org.springframework.mock.web.MockMultipartFile;

/** Chapter 15: a picture and a question in one message, and an exhibit recognised from a photo. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch15Check {
    static final FakeOpenAi AI = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @Autowired
    MockMvc mvc;

    String call(String path, String... params) throws Exception {
        var req = get(path);
        for (int i = 0; i + 1 < params.length; i += 2) req = req.param(params[i], params[i + 1]);
        return mvc.perform(req).andReturn().getResponse().getContentAsString();
    }

    /** All the text of the messages with this role in a request, whether plain or in parts. */
    static String text(JsonNode request, String role) {
        StringBuilder b = new StringBuilder();
        for (JsonNode m : request.path("messages")) {
            if (!role.equals(m.path("role").asString())) continue;
            JsonNode c = m.path("content");
            if (c.isArray()) {
                for (JsonNode p : c) b.append(p.path("text").asString("")).append(" ");
            } else {
                b.append(c.asString("")).append(" ");
            }
        }
        return b.toString();
    }

    static String cut(String s) {
        return s.length() > 160 ? s.substring(0, 160) + "..." : s;
    }

    /** A tiny, valid PNG picture (one pixel). */
    static final byte[] PNG = Base64.getDecoder().decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==");

    String send(String path, String... params) throws Exception {
        var req = multipart(path).file(new MockMultipartFile("image", "photo.png", "image/png", PNG));
        for (int i = 0; i + 1 < params.length; i += 2) req.param(params[i], params[i + 1]);
        return mvc.perform(req).andReturn().getResponse().getContentAsString();
    }

    /** Does the last user message of this request carry the picture, as a JPEG? */
    static boolean hasPicture(JsonNode request) {
        for (JsonNode m : request.path("messages")) {
            if (!"user".equals(m.path("role").asString())) continue;
            for (JsonNode p : m.path("content")) {
                if (p.path("image_url").path("url").asString("").startsWith("data:image/jpeg;base64,")) return true;
            }
        }
        return false;
    }

    @Test
    void imageQuestion() {
        R.task("image_question", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("A brass ball on a long wire: the Foucault pendulum.");
            String answer = send("/look", "q", "What is this exhibit?");
            JsonNode req = AI.chat(-1);
            if (!hasPicture(req)) {
                R.fail("image_question", "the question reached the model without the picture. Put both in one user message: .user(u -> u.text(q).media(type, picture)).");
                return;
            }
            if (!text(req, "user").contains("What is this exhibit?")) {
                R.fail("image_question", "the picture arrived, but the question did not. Send the text and the media together.", "What is this exhibit?", cut(text(req, "user")));
                return;
            }
            if (!answer.contains("Foucault pendulum")) {
                R.fail("image_question", "return the model's answer.", "A brass ball on a long wire: the Foucault pendulum.", cut(answer));
                return;
            }
            R.pass("image_question", "The question and the picture travelled together in one message, as a data URL: Atlas can see.");
        });
    }

    @Test
    void exhibitFromPhoto() {
        R.task("exhibit_from_photo", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("{\"exhibit\": \"Prism room\", \"clue\": \"A rainbow spreads across the floor from a glass prism.\"}");
            JsonNode r = JSON.readTree(send("/identify"));
            if (AI.chatRequests.isEmpty()) {
                R.fail("exhibit_from_photo", "the model was never asked. Send the picture with a question that lists the exhibits.");
                return;
            }
            JsonNode req = AI.chat(-1);
            if (!hasPicture(req)) {
                R.fail("exhibit_from_photo", "the model was asked without the picture: add .media(type, picture) to the user message.");
                return;
            }
            String user = text(req, "user");
            if (!user.contains("Foucault pendulum") || !user.contains("Solar tree")) {
                R.fail("exhibit_from_photo", "the question should list every name in EXHIBITS, so the model picks one of the museum's own exhibits.", "a question listing Foucault pendulum, ..., Solar tree", cut(user));
                return;
            }
            if (!"Prism room".equals(r.path("exhibit").asString(""))) {
                R.fail("exhibit_from_photo", "return the model's answer as a Sighting, with .entity(Sighting.class).", "{\"exhibit\":\"Prism room\", ...}", cut(r.toString()));
                return;
            }
            R.pass("exhibit_from_photo", "A photo in, a Sighting out: the exhibit's name, from the museum's own list, and the clue that gave it away.");
        });
    }
}
