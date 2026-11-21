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

import com.shop.checkout.StockRepository;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@SpringBootTest
@AutoConfigureMockMvc
class Ch22Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    StockRepository stock;
    final ObjectMapper json = new ObjectMapper();

    MvcResult checkout(String body) throws Exception {
        return mvc.perform(post("/checkout").contentType(MediaType.APPLICATION_JSON).content(body)).andReturn();
    }

    int qty(String sku) {
        return stock.findById(sku).orElseThrow().getQuantity();
    }

    @Test
    void checkoutHappyPath() {
        R.task("checkout", () -> {
            int teaBefore = qty("TEA-1");
            MvcResult r = checkout("{\"customerEmail\": \"asha@shop.in\", \"items\": [{\"sku\": \"TEA-1\", \"quantity\": 2}, {\"sku\": \"COF-1\", \"quantity\": 1}]}");
            int code = r.getResponse().getStatus();
            String location = r.getResponse().getHeader("Location");
            if (code == 404 || code == 405) {
                R.fail("checkout", "POST /checkout is not mapped yet.");
                return;
            }
            Map<?, ?> order = r.getResponse().getContentAsString().startsWith("{") ? json.readValue(r.getResponse().getContentAsString(), Map.class) : Map.of();
            if (code != 201 || location == null || !location.matches(".*/orders/[0-9]+$")) {
                R.fail("checkout", "A checkout should answer 201 Created with a Location /orders/{id}.", "201, Location /orders/1", code + ", Location " + location);
            } else if (!Integer.valueOf(7000).equals(order.get("totalPaise"))) {
                R.fail("checkout", "The total should be 2 teas (2 x 2000) plus 1 coffee (3000).", "7000", String.valueOf(order.get("totalPaise")));
            } else if (qty("TEA-1") != teaBefore - 2) {
                R.fail("checkout", "The stock should go down by what was bought.", "TEA-1: " + (teaBefore - 2), "TEA-1: " + qty("TEA-1"));
            } else if (mvc.perform(get(location)).andReturn().getResponse().getStatus() != 200) {
                R.fail("checkout", "The order should be saved and readable at its Location.");
            } else {
                R.pass("checkout", "A real checkout: validated input, stock and order changed in one transaction, and a 201 that points to the new order.");
            }
        });
    }

    @Test
    void checkoutErrors() {
        R.task("checkout_errors", () -> {
            MvcResult bad = checkout("{\"customerEmail\": \"not-an-email\", \"items\": []}");
            Map<?, ?> p = bad.getResponse().getContentAsString().startsWith("{") ? json.readValue(bad.getResponse().getContentAsString(), Map.class) : Map.of();
            int teaBefore = qty("TEA-1");
            MvcResult oos = checkout("{\"customerEmail\": \"ravi@shop.in\", \"items\": [{\"sku\": \"TEA-1\", \"quantity\": 1}, {\"sku\": \"SAM-1\", \"quantity\": 5}]}");
            Map<?, ?> o = oos.getResponse().getContentAsString().startsWith("{") ? json.readValue(oos.getResponse().getContentAsString(), Map.class) : Map.of();
            if (bad.getResponse().getStatus() != 400 || !"Invalid request".equals(p.get("title")) || !(p.get("errors") instanceof Map<?, ?> e) || !e.containsKey("customerEmail") || !e.containsKey("items")) {
                R.fail("checkout_errors", "An invalid checkout should answer 400 with a ProblemDetail titled Invalid request and errors for customerEmail and items.", "400 {\"title\":\"Invalid request\",\"errors\":{...}}", bad.getResponse().getStatus() + " " + bad.getResponse().getContentAsString());
            } else if (oos.getResponse().getStatus() != 409 || !"Out of stock".equals(o.get("title")) || !"SAM-1".equals(o.get("sku"))) {
                R.fail("checkout_errors", "An out-of-stock checkout should answer 409 with a ProblemDetail titled Out of stock and the sku.", "409 {\"title\":\"Out of stock\",\"sku\":\"SAM-1\"}", oos.getResponse().getStatus() + " " + oos.getResponse().getContentAsString());
            } else if (qty("TEA-1") != teaBefore) {
                R.fail("checkout_errors", "The samosas ran out, but the tea was still taken: the checkout must be one transaction.", "TEA-1: " + teaBefore, "TEA-1: " + qty("TEA-1"));
            } else {
                R.pass("checkout_errors", "Every failure is a clear ProblemDetail, and a failed checkout changes nothing. You have built a real Spring Boot API.");
            }
        });
    }
}
