package com.shop.check;

import java.lang.reflect.Constructor;
import java.util.Arrays;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch03Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    ApplicationContext ctx;

    @Test
    void priceService() {
        R.task("price_service", () -> {
            Class<?> calc = Class.forName(ctx.getBean("priceController").getClass().getPackageName() + ".PriceCalculator");
            if (ctx.getBeanNamesForType(calc).length == 0) {
                R.fail("price_service", "PriceCalculator is not a bean yet: Spring has not created one. Put @Service on the class.");
                return;
            }
            boolean injected = Arrays.stream(ctx.getBean("priceController").getClass().getConstructors())
                    .map(Constructor::getParameterTypes).anyMatch(ps -> Arrays.asList(ps).contains(calc));
            String got = mvc.perform(get("/kulfi/price")).andReturn().getResponse().getContentAsString();
            if (!injected) {
                R.fail("price_service", "PriceController does not ask for a PriceCalculator in its constructor yet.", "2360", got);
            } else if (got.equals("2360")) {
                R.pass("price_service", "Spring created one PriceCalculator and passed it to PriceController's constructor: dependency injection, with no new in sight.");
            } else {
                R.fail("price_service", "GET /kulfi/price should be 2000 paise plus 18% GST.", "2360", got);
            }
        });
    }

    @Test
    void oneCounter() {
        R.task("one_counter", () -> {
            int before = Integer.parseInt(mvc.perform(get("/stats")).andReturn().getResponse().getContentAsString());
            mvc.perform(get("/"));
            mvc.perform(get("/"));
            int after = Integer.parseInt(mvc.perform(get("/stats")).andReturn().getResponse().getContentAsString());
            if (after - before == 2) {
                R.pass("one_counter", "Both controllers share the one VisitCounter Spring made: a bean is a single object, shared by everyone who asks for it.");
            } else {
                R.fail("one_counter", "Two visits to / did not show up in /stats: HomeController still counts on a VisitCounter of its own (made with new). Ask for it in the constructor instead.", "2 more visits", (after - before) + " more");
            }
        });
    }
}
