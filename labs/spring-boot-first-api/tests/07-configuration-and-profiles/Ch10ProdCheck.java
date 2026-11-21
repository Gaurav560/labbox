package com.shop.check;

import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("prod")
class Ch10ProdCheck {
    @Autowired
    MockMvc mvc;

    @Test
    void prodProfile() {
        R.task("prod_profile", () -> {
            String body = mvc.perform(get("/shop/info")).andReturn().getResponse().getContentAsString();
            Map<?, ?> info = new ObjectMapper().readValue(body, Map.class);
            if (!"Shop API (production)".equals(info.get("name")) || !Integer.valueOf(100000).equals(info.get("freeDeliveryAbovePaise"))) {
                R.fail("prod_profile", "With the prod profile active, the shop settings should come from application-prod.yml.", "{\"name\":\"Shop API (production)\",\"freeDeliveryAbovePaise\":100000}", body);
            } else {
                R.pass("prod_profile", "Same code, different settings: the prod profile layered application-prod.yml over application.yml.");
            }
        });
    }
}
