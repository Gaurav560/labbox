package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch06Check {
    @Autowired
    MockMvc mvc;

    @Test
    void primaryGateway() {
        R.task("primary_gateway", () -> {
            String body = mvc.perform(get("/pay/5000")).andReturn().getResponse().getContentAsString();
            if (body.equals("Paid Rs 50 by UPI")) {
                R.pass("primary_gateway", "Two beans fit, and @Primary told Spring which one to inject by default: the app starts and pays by UPI.");
            } else {
                R.fail("primary_gateway", "GET /pay/5000 should pay with the UPI gateway.", "Paid Rs 50 by UPI", body);
            }
        });
    }

    @Test
    void allGateways() {
        R.task("all_gateways", () -> {
            String body = mvc.perform(get("/gateways")).andReturn().getResponse().getContentAsString().replace(" ", "");
            if (body.equals("[\"card\",\"upi\"]")) {
                R.pass("all_gateways", "Spring put every PaymentGateway bean into your List: add a wallet gateway tomorrow, and it appears here with no other change.");
            } else if (body.equals("[]")) {
                R.fail("all_gateways", "GET /gateways still returns an empty list. Take a List<PaymentGateway> in a constructor and return the names.", "[\"card\",\"upi\"]", body);
            } else {
                R.fail("all_gateways", "GET /gateways should list the names of all gateways, A to Z.", "[\"card\",\"upi\"]", body);
            }
        });
    }
}
