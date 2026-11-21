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

import org.springframework.dao.DataIntegrityViolationException;

import com.shop.product.Product;
import com.shop.product.ProductRepository;

@SpringBootTest
@AutoConfigureMockMvc
class Ch11Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    ProductRepository repository;

    @Test
    void productEntity() {
        R.task("product_entity", () -> {
            String body = mvc.perform(get("/products")).andReturn().getResponse().getContentAsString();
            List<Map<String, Object>> list = new ObjectMapper().readValue(body, new TypeReference<>() {});
            List<Object> names = list.stream().map(m -> m.get("name")).toList();
            if (!names.equals(List.of("Masala tea", "Filter coffee", "Samosa")) || list.get(0).get("id") == null) {
                R.fail("product_entity", "GET /products should return the three products from data.sql, each with an id.", "[Masala tea, Filter coffee, Samosa]", names.toString());
            } else {
                R.pass("product_entity", "Product is an entity: Hibernate created its table, data.sql filled it, and Spring Data read it back, with no SQL written by you.");
            }
        });
    }

    @Test
    void uniqueSku() {
        R.task("unique_sku", () -> {
            boolean duplicateRefused;
            try {
                repository.saveAndFlush(new Product("Copy of tea", 1000, "TEA-1"));
                duplicateRefused = false;
            } catch (DataIntegrityViolationException e) {
                duplicateRefused = true;
            }
            boolean nullRefused;
            try {
                repository.saveAndFlush(new Product("No sku", 1000, null));
                nullRefused = false;
            } catch (DataIntegrityViolationException e) {
                nullRefused = true;
            }
            if (!duplicateRefused) {
                R.fail("unique_sku", "The database accepted a second product with sku TEA-1. Mark the sku column unique.");
            } else if (!nullRefused) {
                R.fail("unique_sku", "The database accepted a product without a sku. Mark the column as not nullable.");
            } else {
                R.pass("unique_sku", "@Column(unique = true, nullable = false) became database constraints: even code that skips your checks cannot store a duplicate.");
            }
        });
    }
}
