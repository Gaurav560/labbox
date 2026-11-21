package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch02Check {
    @Autowired
    MockMvc mvc;

    @Test
    void componentScan() {
        R.task("component_scan", () -> {
            MvcResult r = mvc.perform(get("/status")).andReturn();
            if (r.getResponse().getStatus() == 200 && r.getResponse().getContentAsString().equals("ok")) {
                R.pass("component_scan", "Component scanning found StatusController: it now lives under com.shop, the package @SpringBootApplication scans.");
            } else {
                R.fail("component_scan", "GET /status still returns " + r.getResponse().getStatus() + ". Spring only scans com.shop and the packages under it: move StatusController there (and fix its package line).", "200 ok", String.valueOf(r.getResponse().getStatus()));
            }
        });
    }

    @Test
    void greetingProperty() {
        R.task("greeting_property", () -> {
            String got = mvc.perform(get("/greeting")).andReturn().getResponse().getContentAsString();
            if (got.equals("Welcome to the Shop API")) {
                R.pass("greeting_property", "Spring read shop.greeting from application.properties and injected it with @Value: change the file, not the code.");
            } else if (got.equals("not set")) {
                R.fail("greeting_property", "shop.greeting is not in application.properties yet, so @Value used its default.", "Welcome to the Shop API", got);
            } else {
                R.fail("greeting_property", "The greeting is not quite right.", "Welcome to the Shop API", got);
            }
        });
    }
}
