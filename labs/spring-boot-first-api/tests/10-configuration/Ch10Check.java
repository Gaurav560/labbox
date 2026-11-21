package com.shop.check;

import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch10Check {
    @Autowired
    MockMvc mvc;

    @Test
    void shopProperties() {
        R.task("shop_properties", () -> {
            String body = mvc.perform(get("/shop/info")).andReturn().getResponse().getContentAsString();
            Map<?, ?> info = new ObjectMapper().readValue(body, Map.class);
            if (!"Shop API".equals(info.get("name")) || !Integer.valueOf(50000).equals(info.get("freeDeliveryAbovePaise"))) {
                R.fail("shop_properties", "GET /shop/info should show the values from application.yml, read through ShopProperties.", "{\"name\":\"Shop API\",\"freeDeliveryAbovePaise\":50000}", body);
            } else {
                R.pass("shop_properties", "@ConfigurationProperties bound shop.* to a typed record, and free-delivery-above-paise matched freeDeliveryAbovePaise by itself.");
            }
        });
    }
}
