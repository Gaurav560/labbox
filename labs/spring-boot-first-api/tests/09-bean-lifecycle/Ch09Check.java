package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch09Check {
    @Autowired
    MockMvc mvc;

    @Test
    void postConstruct() {
        R.task("post_construct", () -> {
            String count = mvc.perform(get("/prices/count")).andReturn().getResponse().getContentAsString();
            var kulfi = mvc.perform(get("/prices/KUL-1")).andReturn().getResponse();
            if (!"3".equals(count)) {
                R.fail("post_construct", "The catalogue is empty: load() is never called. Mark it so Spring calls it once, right after creating the bean.", "3 prices", count + " prices");
            } else if (kulfi.getStatus() != 200 || !"2000".equals(kulfi.getContentAsString())) {
                R.fail("post_construct", "GET /prices/KUL-1 should answer 2000.", "2000", kulfi.getStatus() + " " + kulfi.getContentAsString());
            } else {
                R.pass("post_construct", "The prices were loaded once, at start-up, after Spring created the bean: no request ever waits for the file.");
            }
        });
    }

    @Test
    void prototypeScope() {
        R.task("prototype_scope", () -> {
            mvc.perform(get("/receipt/Mango kulfi")).andReturn();
            String second = mvc.perform(get("/receipt/Samosa")).andReturn().getResponse().getContentAsString().replace(" ", "");
            if (second.equals("[\"1xSamosa\"]")) {
                R.pass("prototype_scope", "Each customer now gets a brand new receipt: prototype scope makes Spring create a fresh bean every time one is asked for.");
            } else {
                R.fail("prototype_scope", "The second customer's receipt still shows the first customer's kulfi: every request gets the same shared ReceiptPrinter.", "[\"1 x Samosa\"]", second);
            }
        });
    }
}
