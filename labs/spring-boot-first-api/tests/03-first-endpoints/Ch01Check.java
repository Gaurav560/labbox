package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch01Check {
    @Autowired
    MockMvc mvc;

    @Test
    void hello() {
        R.task("hello", () -> {
            MvcResult r = mvc.perform(get("/hello")).andReturn();
            int code = r.getResponse().getStatus();
            String body = r.getResponse().getContentAsString();
            if (code == 404) {
                R.fail("hello", "GET /hello returned 404: there is no method mapped to /hello yet.", "200", "404");
            } else if (code == 200 && (body.equals("Hello from the Shop API!") || body.equals("Hello from PaySetu!"))) {
                R.pass("hello", "Your first endpoint: @GetMapping told Spring to call your method for GET /hello, and Spring sent its String back as the response.");
            } else {
                R.fail("hello", "GET /hello answered, but with different text. Mind the capital letters and the !.", "200 Hello from the Shop API!", code + " " + body);
            }
        });
    }

    @Test
    void merchants() {
        R.task("merchants", () -> {
            MvcResult r = mvc.perform(get("/merchants")).andReturn();
            int code = r.getResponse().getStatus();
            String body = r.getResponse().getContentAsString().replace(" ", "");
            String want = "[\"AnnapurnaMess\",\"BookPoint\",\"KiranaKing\"]";
            if (code == 404) {
                R.fail("merchants", "GET /merchants returned 404: there is no method mapped to /merchants yet.", "200", "404");
            } else if (code == 200 && body.equals(want)) {
                R.pass("merchants", "You returned a List and Spring turned it into a JSON array for you, sorted A to Z.");
            } else if (code == 200 && body.contains("Kirana") && !body.equals(want)) {
                R.fail("merchants", "The names are there, but not in A to Z order. Sort a copy of the list before returning it.", want, body);
            } else {
                R.fail("merchants", "GET /merchants should return the names A to Z as a JSON array.", want, code + " " + body);
            }
        });
    }
}
