package com.shop.check;

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
class Ch09Check {
    @Autowired
    MockMvc mvc;
    final ObjectMapper json = new ObjectMapper();

    @Test
    void notFoundProblem() {
        R.task("not_found_problem", () -> {
            MvcResult r = mvc.perform(get("/products/99")).andReturn();
            String body = r.getResponse().getContentAsString();
            Map<?, ?> p = body.startsWith("{") ? json.readValue(body, Map.class) : Map.of();
            if (r.getResponse().getStatus() != 404) {
                R.fail("not_found_problem", "GET /products/99 answers " + r.getResponse().getStatus() + ": ProductNotFoundException is not handled yet, so Spring answers 500.", "404", String.valueOf(r.getResponse().getStatus()));
            } else if (!"Product not found".equals(p.get("title")) || !"No product 99".equals(p.get("detail"))) {
                R.fail("not_found_problem", "The 404 should be a ProblemDetail with the title Product not found and the exception's message as detail.", "{\"title\":\"Product not found\",\"status\":404,\"detail\":\"No product 99\"}", body);
            } else {
                R.pass("not_found_problem", "One @ExceptionHandler, and every endpoint that cannot find a product answers the same clear 404.");
            }
        });
    }

    @Test
    void validationProblem() {
        R.task("validation_problem", () -> {
            MvcResult r = mvc.perform(post("/products").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"\", \"pricePaise\": -1}")).andReturn();
            String body = r.getResponse().getContentAsString();
            Map<?, ?> p = body.startsWith("{") ? json.readValue(body, Map.class) : Map.of();
            Object errors = p.get("errors");
            if (r.getResponse().getStatus() != 400) {
                R.fail("validation_problem", "An invalid product should still answer 400.", "400", String.valueOf(r.getResponse().getStatus()));
            } else if (!"Invalid request".equals(p.get("title")) || !(errors instanceof Map<?, ?> m) || !m.containsKey("name") || !m.containsKey("pricePaise")) {
                R.fail("validation_problem", "The 400 should be a ProblemDetail titled Invalid request, with an errors map naming each bad field (name and pricePaise).", "{\"title\":\"Invalid request\",\"errors\":{\"name\":...,\"pricePaise\":...}}", body);
            } else {
                R.pass("validation_problem", "A client now sees exactly which fields are wrong and why, in the same format as every other error.");
            }
        });
    }
}
