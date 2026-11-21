package com.shop.check;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.Arrays;

import com.shop.product.ProductRepository;

@SpringBootTest
@AutoConfigureMockMvc
class Ch12Check {
    @Autowired
    MockMvc mvc;

    static boolean declares(String name) {
        return Arrays.stream(ProductRepository.class.getDeclaredMethods()).anyMatch(m -> m.getName().equals(name));
    }

    @Test
    void findByCategory() {
        R.task("find_by_category", () -> {
            String body = mvc.perform(get("/products?category=snacks")).andReturn().getResponse().getContentAsString();
            List<Map<String, Object>> list = new ObjectMapper().readValue(body, new TypeReference<>() {});
            List<Object> names = list.stream().map(m -> m.get("name")).toList();
            if (!declares("findByCategoryOrderByNameAsc")) {
                R.fail("find_by_category", "ProductRepository has no derived query findByCategoryOrderByNameAsc yet.");
            } else if (!names.equals(List.of("Bhel puri", "Kachori", "Samosa"))) {
                R.fail("find_by_category", "GET /products?category=snacks should list the snacks sorted by name.", "[Bhel puri, Kachori, Samosa]", names.toString());
            } else {
                R.pass("find_by_category", "Spring Data read the method name and wrote the SQL: WHERE category = ? ORDER BY name.");
            }
        });
    }

    @Test
    void skuConflict() {
        R.task("sku_conflict", () -> {
            int dup = mvc.perform(post("/products").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Tea again\", \"pricePaise\": 900, \"category\": \"drinks\", \"sku\": \"TEA-1\"}")).andReturn().getResponse().getStatus();
            int fresh = mvc.perform(post("/products").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Lassi\", \"pricePaise\": 3500, \"category\": \"drinks\", \"sku\": \"LAS-1\"}")).andReturn().getResponse().getStatus();
            if (!declares("existsBySku")) {
                R.fail("sku_conflict", "ProductRepository has no existsBySku yet.");
            } else if (dup != 409) {
                R.fail("sku_conflict", "Posting a product with an existing sku should answer 409 Conflict.", "409", String.valueOf(dup));
            } else if (fresh != 201) {
                R.fail("sku_conflict", "A product with a new sku should still be created.", "201", String.valueOf(fresh));
            } else {
                R.pass("sku_conflict", "existsBySku runs a cheap SELECT, and a clash is a clear 409 instead of a database error.");
            }
        });
    }
}
