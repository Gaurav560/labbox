package com.shop;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.shopkit.greeting.Greeter;

/** The Shop API's own beans. The shop wants its own greeting, not ShopKit's default one. */
@Configuration
public class ShopConfig {

    @Bean
    public Greeter shopGreeter() {
        return new Greeter("Welcome to the Shop API");
    }
}
