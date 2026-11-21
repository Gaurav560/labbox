package com.shopkit.greeting;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;

/**
 * ShopKit's auto-configuration: sensible beans for any app that has ShopKit on its classpath, the same way
 * Spring Boot's own auto-configurations work. Listed in META-INF/spring/...AutoConfiguration.imports.
 */
@AutoConfiguration
public class GreetingAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public Greeter defaultGreeter() {
        return new Greeter("Hello from ShopKit");
    }

    @Bean
    @ConditionalOnProperty(prefix = "shop.festival", name = "enabled", havingValue = "true")
    public FestivalBanner festivalBanner() {
        return new FestivalBanner("Diwali sale: 20% off sweets!");
    }
}
