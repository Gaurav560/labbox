package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.AutoConfigurations;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.test.web.servlet.MockMvc;

import com.shopkit.greeting.FestivalBanner;
import com.shopkit.greeting.Greeter;
import com.shopkit.greeting.GreetingAutoConfiguration;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch08Check {
    @Autowired
    MockMvc mvc;

    /** ShopKit's auto-configuration on its own, the way Spring Boot tests its own auto-configurations. */
    final ApplicationContextRunner shopkit = new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(GreetingAutoConfiguration.class));

    @Test
    void backsOff() {
        R.task("backs_off", () -> {
            String body = mvc.perform(get("/greeting")).andReturn().getResponse().getContentAsString();
            String[] alone = new String[1];
            shopkit.run(ctx -> alone[0] = ctx.getBeansOfType(Greeter.class).size() == 1 ? ctx.getBean(Greeter.class).greet() : "none");
            if (!body.equals("Welcome to the Shop API")) {
                R.fail("backs_off", "GET /greeting should use the shop's own Greeter.", "Welcome to the Shop API", body);
            } else if (!"Hello from ShopKit".equals(alone[0])) {
                R.fail("backs_off", "In an app with no Greeter of its own, ShopKit should still give its default one.", "Hello from ShopKit", alone[0]);
            } else {
                R.pass("backs_off", "ShopKit's Greeter steps aside when the app defines one, and fills in when it does not: exactly how Spring Boot's own defaults behave.");
            }
        });
    }

    @Test
    void onProperty() {
        R.task("on_property", () -> {
            boolean[] off = new boolean[1];
            boolean[] on = new boolean[1];
            shopkit.withPropertyValues("shop.festival.enabled=false").run(ctx -> off[0] = ctx.getBeansOfType(FestivalBanner.class).isEmpty());
            shopkit.run(ctx -> off[0] = off[0] && ctx.getBeansOfType(FestivalBanner.class).isEmpty());
            shopkit.withPropertyValues("shop.festival.enabled=true").run(ctx -> on[0] = ctx.getBeansOfType(FestivalBanner.class).size() == 1);
            String body = mvc.perform(get("/banner")).andReturn().getResponse().getContentAsString();
            if (!off[0]) {
                R.fail("on_property", "The banner bean is created even when shop.festival.enabled is false or not set. Make it conditional on that property.");
            } else if (!on[0]) {
                R.fail("on_property", "With shop.festival.enabled=true there should be a banner bean, but there is none. Check the prefix, name and havingValue.");
            } else if (!body.startsWith("Diwali")) {
                R.fail("on_property", "The banner is conditional now, but this app has not switched the festival on. Set the property in application.properties.", "Diwali sale: 20% off sweets!", body);
            } else {
                R.pass("on_property", "A setting decides whether a bean exists at all: that is how one property switches whole Spring Boot features on and off.");
            }
        });
    }
}
