package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch18Check {
    @Autowired
    MockMvc mvc;

    @Test
    void requestIdFilter() {
        R.task("request_id_filter", () -> {
            String fresh1 = mvc.perform(get("/api/products")).andReturn().getResponse().getHeader("X-Request-Id");
            String fresh2 = mvc.perform(get("/ping")).andReturn().getResponse().getHeader("X-Request-Id");
            String echoed = mvc.perform(get("/api/products").header("X-Request-Id", "order-42")).andReturn().getResponse().getHeader("X-Request-Id");
            if (fresh1 == null || fresh1.isBlank()) {
                R.fail("request_id_filter", "Responses have no X-Request-Id header yet. Set it on the response in the filter, before chain.doFilter.", "X-Request-Id: <an id>", "(no header)");
            } else if (fresh1.equals(fresh2)) {
                R.fail("request_id_filter", "Two requests got the same id. Make a new one for each request (UUID.randomUUID()).", "two different ids", fresh1 + " twice");
            } else if (!"order-42".equals(echoed)) {
                R.fail("request_id_filter", "When the client sends X-Request-Id, pass that same id back, so the id follows the request everywhere.", "order-42", String.valueOf(echoed));
            } else {
                R.pass("request_id_filter", "Every response carries a request id, new or the client's own: the filter ran before Spring MVC for every request, even /ping.");
            }
        });
    }

    @Test
    void handledByInterceptor() {
        R.task("handled_by_interceptor", () -> {
            String api = mvc.perform(get("/api/products")).andReturn().getResponse().getHeader("X-Handled-By");
            String ping = mvc.perform(get("/ping")).andReturn().getResponse().getHeader("X-Handled-By");
            if (api == null) {
                R.fail("handled_by_interceptor", "GET /api/products has no X-Handled-By header: the interceptor is not registered yet.", "X-Handled-By: ProductController#all", "(no header)");
            } else if (ping != null) {
                R.fail("handled_by_interceptor", "/ping also got the header: register the interceptor for /api/** only.", "(no header on /ping)", "X-Handled-By: " + ping);
            } else {
                R.pass("handled_by_interceptor", "The interceptor knows which controller method handles the request, and runs only for the API's paths.");
            }
        });
    }
}
