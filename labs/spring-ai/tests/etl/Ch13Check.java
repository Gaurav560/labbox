package com.atlas.check;

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
import java.util.stream.Collectors;

import com.atlas.ExhibitEtl;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

/** Chapter 13: extract, transform and load the exhibit cards. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch13Check {
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

    @Autowired
    ExhibitEtl etl;

    @Autowired
    VectorStore store;

    @Test
    void readCards() {
        R.task("read_cards", () -> {
            var cards = new PathMatchingResourcePatternResolver().getResources("classpath:exhibits/*.md");
            var docs = etl.read(cards);
            if (docs.isEmpty()) {
                R.fail("read_cards", "read(...) returned no documents. Read each card with new MarkdownDocumentReader(card, config).get().");
                return;
            }
            var files = docs.stream().map(d -> String.valueOf(d.getMetadata().get("file"))).collect(Collectors.toSet());
            if (files.size() != 12 || files.stream().anyMatch(f -> !f.endsWith(".md"))) {
                R.fail("read_cards", "every document should know its card's file name, in the metadata key file. MarkdownDocumentReaderConfig.builder().withAdditionalMetadata(\"file\", card.getFilename()).", "12 different .md files", files.size() + " values: " + files.stream().limit(3).toList());
                return;
            }
            if (docs.stream().noneMatch(d -> d.getText().contains("15 metre steel wire"))) {
                R.fail("read_cards", "the documents do not contain the cards' text.");
                return;
            }
            R.pass("read_cards", "12 cards read into " + docs.size() + " documents, each labelled with its file.");
        });
    }

    @Test
    void splitAndLoad() {
        R.task("split_and_load", () -> {
            JsonNode report = JSON.readTree(call("/etl"));
            int documents = report.path("documents").asInt(), chunks = report.path("chunks").asInt();
            var stored = store.similaritySearch(SearchRequest.builder().query("gallery").topK(500).similarityThresholdAll().build());
            if (stored.isEmpty()) {
                R.fail("split_and_load", "the vector store is empty. After splitting, add the chunks with store.add(...).", "chunks in the store", "nothing");
                return;
            }
            if (chunks <= documents || stored.size() != chunks) {
                R.fail("split_and_load", "the cards were not split into chunks of at most 100 tokens. TokenTextSplitter.builder().withChunkSize(100).build().apply(documents).", "more chunks than documents, all in the store", documents + " documents, " + chunks + " chunks, " + stored.size() + " stored");
                return;
            }
            int longest = stored.stream().mapToInt(d -> d.getText().length()).max().orElse(0);
            if (longest > 700) {
                R.fail("split_and_load", "some chunks are far longer than 100 tokens.", "chunks of about 100 tokens (400 to 600 characters)", "the longest has " + longest + " characters");
                return;
            }
            if (stored.stream().anyMatch(d -> d.getMetadata().get("file") == null)) {
                R.fail("split_and_load", "some chunks lost the file name. The splitter copies metadata; make sure the documents had it before splitting.");
                return;
            }
            R.pass("split_and_load", documents + " documents became " + chunks + " chunks of about 100 tokens, each still knowing its file, all in the store.");
        });
    }
}
