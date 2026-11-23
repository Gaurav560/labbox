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

import jakarta.persistence.EntityManagerFactory;
import org.hibernate.SessionFactory;
import org.hibernate.stat.Statistics;

@SpringBootTest(properties = "spring.jpa.properties.hibernate.generate_statistics=true")
@AutoConfigureMockMvc
class Ch13Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    EntityManagerFactory emf;

    @Test
    void orderItems() {
        R.task("order_items", () -> {
            String body = mvc.perform(get("/orders/1")).andReturn().getResponse().getContentAsString();
            Map<?, ?> o = body.startsWith("{") ? new ObjectMapper().readValue(body, Map.class) : Map.of();
            if (!Integer.valueOf(2).equals(o.get("items")) || !Integer.valueOf(9400).equals(o.get("totalPaise"))) {
                R.fail("order_items", "Order 1 should have its 2 items (2 kulfi, 3 samosas), totalling 9400 paise.", "{\"items\":2,\"totalPaise\":9400}", body);
            } else {
                R.pass("order_items", "@OneToMany and @ManyToOne map the order_id foreign key in both directions: order.getItems() just works.");
            }
        });
    }

    @Test
    void fixNPlusOne() {
        R.task("fix_n_plus_one", () -> {
            Statistics stats = emf.unwrap(SessionFactory.class).getStatistics();
            stats.clear();
            String body = mvc.perform(get("/orders")).andReturn().getResponse().getContentAsString();
            long queries = stats.getPrepareStatementCount();
            if (!body.contains("Zoya")) {
                R.fail("fix_n_plus_one", "GET /orders should still list all five orders.");
            } else if (queries > 2) {
                R.fail("fix_n_plus_one", "GET /orders ran " + queries + " SQL queries: one for the orders, then one more per order for its items (N+1). Load them together with JOIN FETCH.", "1 query", queries + " queries");
            } else {
                R.pass("fix_n_plus_one", "One query instead of " + 6 + ": JOIN FETCH loaded every order with its items in a single SELECT.");
            }
        });
    }
}
