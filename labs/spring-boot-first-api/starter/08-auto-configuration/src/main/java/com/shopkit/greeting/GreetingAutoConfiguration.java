package com.shopkit.greeting;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.context.annotation.Bean;

/**
 * ShopKit's auto-configuration: sensible beans for any app that has ShopKit on its classpath, the same way
 * Spring Boot's own auto-configurations work. Listed in META-INF/spring/...AutoConfiguration.imports.
 */
@AutoConfiguration
public class GreetingAutoConfiguration {

    // TODO (task backs_off): a default Greeter, but only if the app has not defined its own Greeter bean.
    @Bean
    public Greeter defaultGreeter() {
        return new Greeter("Hello from ShopKit");
    }

    // TODO (task on_property): only create the banner when the setting shop.festival.enabled is true.
    @Bean
    public FestivalBanner festivalBanner() {
        return new FestivalBanner("Diwali sale: 20% off sweets!");
    }
}
