package com.shop.check;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@SpringBootTest
@AutoConfigureMockMvc
class Ch06Check {
    @Autowired
    MockMvc mvc;
    final ObjectMapper json = new ObjectMapper();

    @Test
    void createProduct() {
        R.task("create_product", () -> {
            MvcResult r = mvc.perform(post("/products").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Vada pav\", \"pricePaise\": 2500}")).andReturn();
            int code = r.getResponse().getStatus();
            if (code == 405 || code == 404) {
                R.fail("create_product", "POST /products is not mapped yet (" + code + "). Add a @PostMapping method with a @RequestBody NewProduct parameter.");
                return;
            }
            Map<?, ?> made = json.readValue(r.getResponse().getContentAsString(), Map.class);
            String list = mvc.perform(get("/products")).andReturn().getResponse().getContentAsString();
            if (!"Vada pav".equals(made.get("name")) || !Integer.valueOf(2500).equals(made.get("pricePaise"))) {
                R.fail("create_product", "The response should be the stored product, with the name and price you sent.", "{\"name\":\"Vada pav\",\"pricePaise\":2500,...}", r.getResponse().getContentAsString());
            } else if (!(made.get("id") instanceof Number) || !list.contains("Vada pav")) {
                R.fail("create_product", "The product must be stored with repository.add(...), so it gets an id and appears in GET /products.");
            } else {
                R.pass("create_product", "@RequestBody: Jackson read the JSON into a NewProduct record, and the stored product went back as JSON.");
            }
        });
    }

    @Test
    void productView() {
        R.task("product_view", () -> {
            MvcResult r = mvc.perform(get("/products/1/view")).andReturn();
            String body = r.getResponse().getContentAsString();
            Map<?, ?> v = r.getResponse().getStatus() == 200 ? json.readValue(body, Map.class) : Map.of();
            int missing = mvc.perform(get("/products/99/view")).andReturn().getResponse().getStatus();
            if (v.containsKey("costPaise")) {
                R.fail("product_view", "The view still includes costPaise, the shop's internal cost. Return a ProductView instead of the Product.", "{\"id\":1,\"name\":\"Mango lassi\",\"price\":\"Rs 20.00\"}", body);
            } else if (!"Rs 20.00".equals(v.get("price")) || !"Mango lassi".equals(v.get("name"))) {
                R.fail("product_view", "The view should show the name and the price formatted as Rs 20.00.", "{\"id\":1,\"name\":\"Mango lassi\",\"price\":\"Rs 20.00\"}", body);
            } else if (missing != 404) {
                R.fail("product_view", "An unknown id should still answer 404.", "404", String.valueOf(missing));
            } else {
                R.pass("product_view", "A DTO decides exactly what the API shows: the internal cost never leaves the server.");
            }
        });
    }
}
