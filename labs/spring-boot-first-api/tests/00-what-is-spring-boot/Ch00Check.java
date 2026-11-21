package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class Ch00Check {
    @Value("${spring.application.name:}")
    String name;

    @Test
    void appName() {
        R.task("app_name", () -> {
            if ("shop-api".equals(name)) {
                R.pass("app_name", "Your first setting: Spring read application.properties when the app started, and the app is now called shop-api.");
            } else if (name.isEmpty()) {
                R.fail("app_name", "spring.application.name is not set yet. Add the line spring.application.name=shop-api to application.properties.", "shop-api", "(not set)");
            } else {
                R.fail("app_name", "The name is not quite right.", "shop-api", name);
            }
        });
    }
}
