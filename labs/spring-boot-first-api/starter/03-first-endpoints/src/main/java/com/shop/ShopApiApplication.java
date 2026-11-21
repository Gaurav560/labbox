package com.shop;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// The entry point: SpringApplication.run starts the Spring container and the web server.
@SpringBootApplication
public class ShopApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(ShopApiApplication.class, args);
    }
}
