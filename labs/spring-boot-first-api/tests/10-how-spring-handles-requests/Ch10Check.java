package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext
class Ch10Check {
    @Autowired
    MockMvc mvc;

    @Test
    void classPrefix() {
        R.task("class_prefix", () -> {
            int versioned = mvc.perform(get("/api/v1/cart")).andReturn().getResponse().getStatus();
            int added = mvc.perform(post("/api/v1/cart/items/lassi")).andReturn().getResponse().getStatus();
            int old = mvc.perform(get("/cart")).andReturn().getResponse().getStatus();
            if (versioned != 200 || added != 200) {
                R.fail("class_prefix", "GET /api/v1/cart and POST /api/v1/cart/items/lassi should both work: put the /api/v1 prefix on the class.", "200 and 200", versioned + " and " + added);
            } else if (old != 404) {
                R.fail("class_prefix", "GET /cart still answers: the old path should be gone once the prefix is on the class.", "404", String.valueOf(old));
            } else {
                R.pass("class_prefix", "One @RequestMapping on the class, and every endpoint below it moved under /api/v1.");
            }
        });
    }

    @Test
    void methodRouting() {
        R.task("method_routing", () -> {
            mvc.perform(post("/api/v1/cart/items/samosa")).andReturn();
            var del = mvc.perform(delete("/api/v1/cart")).andReturn().getResponse();
            String after = mvc.perform(get("/api/v1/cart")).andReturn().getResponse().getContentAsString();
            if (del.getStatus() == 404 && mvc.perform(get("/api/v1/cart")).andReturn().getResponse().getStatus() == 404) {
                R.fail("method_routing", "/api/v1/cart is not mapped yet: do the class prefix task first.");
            } else if (del.getStatus() == 405) {
                R.fail("method_routing", "DELETE /api/v1/cart answers 405 Method Not Allowed: the path exists for GET, but no method handles DELETE yet.", "200", "405");
            } else if (del.getStatus() != 200 || !"[]".equals(after)) {
                R.fail("method_routing", "DELETE /api/v1/cart should empty the cart.", "200, then GET answers []", del.getStatus() + ", then GET answers " + after);
            } else {
                R.pass("method_routing", "Same path, different methods, different Java methods: Spring routes on the method and the path together.");
            }
        });
    }
}
