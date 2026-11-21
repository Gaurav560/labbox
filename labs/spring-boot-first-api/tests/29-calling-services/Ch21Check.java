package com.shop.check;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch21Check {
    /** A fake supplier: TEA-1 has 120, MISSING is not stocked (404), SLOW answers after 3 seconds. */
    static final HttpServer SUPPLIER;

    static {
        try {
            SUPPLIER = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        SUPPLIER.createContext("/stock/", ex -> {
            String sku = ex.getRequestURI().getPath().substring("/stock/".length());
            int code = 200;
            String body = "{\"sku\": \"" + sku + "\", \"available\": 120}";
            if (sku.equals("MISSING")) {
                code = 404;
                body = "{\"error\": \"not stocked\"}";
            } else if (sku.equals("SLOW")) {
                try {
                    Thread.sleep(3000);
                } catch (InterruptedException ignored) {
                    Thread.currentThread().interrupt();
                }
            }
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().add("Content-Type", "application/json");
            ex.sendResponseHeaders(code, bytes.length);
            ex.getResponseBody().write(bytes);
            ex.close();
        });
        SUPPLIER.setExecutor(java.util.concurrent.Executors.newCachedThreadPool());
        SUPPLIER.start();
    }

    @DynamicPropertySource
    static void supplierUrl(DynamicPropertyRegistry registry) {
        registry.add("supplier.base-url", () -> "http://127.0.0.1:" + SUPPLIER.getAddress().getPort());
    }

    @AfterAll
    static void stop() {
        SUPPLIER.stop(0);
    }

    @Autowired
    MockMvc mvc;

    @Test
    void fetchStock() {
        R.task("fetch_stock", () -> {
            MvcResult r = mvc.perform(get("/supplier-stock/TEA-1")).andReturn();
            String body = r.getResponse().getContentAsString().replace(" ", "");
            if (r.getResponse().getStatus() == 200 && body.contains("\"available\":120")) {
                R.pass("fetch_stock", "RestClient called the supplier, and Jackson read its JSON into a SupplierStock record.");
            } else {
                R.fail("fetch_stock", "GET /supplier-stock/TEA-1 should show the 120 the supplier reports.", "{\"available\":120,...}", r.getResponse().getStatus() + " " + body);
            }
        });
    }

    @Test
    void handleSupplierErrors() {
        R.task("handle_supplier_errors", () -> {
            MvcResult missing = mvc.perform(get("/supplier-stock/MISSING")).andReturn();
            long start = System.currentTimeMillis();
            MvcResult slow = mvc.perform(get("/supplier-stock/SLOW")).andReturn();
            long took = System.currentTimeMillis() - start;
            String m = missing.getResponse().getContentAsString().replace(" ", "");
            if (missing.getResponse().getStatus() != 200 || !m.contains("\"available\":0")) {
                R.fail("handle_supplier_errors", "When the supplier answers 404, the item is simply not stocked: answer 200 with available 0.", "200 {\"available\":0}", missing.getResponse().getStatus() + " " + m);
            } else if (took > 2500) {
                R.fail("handle_supplier_errors", "A slow supplier held the request for " + took + " ms. Give the client a 1 second read timeout.", "under 2000 ms", took + " ms");
            } else if (slow.getResponse().getStatus() != 503) {
                R.fail("handle_supplier_errors", "When the supplier is too slow, answer 503 Service Unavailable.", "503", String.valueOf(slow.getResponse().getStatus()));
            } else {
                R.pass("handle_supplier_errors", "A 404 means \"not stocked\", and a slow supplier fails fast with 503 instead of hanging the shop.");
            }
        });
    }
}
