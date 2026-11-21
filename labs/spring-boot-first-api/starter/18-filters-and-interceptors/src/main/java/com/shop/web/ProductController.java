package com.shop.web;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    @GetMapping("/api/products")
    public List<String> all() {
        return List.of("Masala tea", "Samosa", "Filter coffee");
    }

    /** Not part of the API: a simple "are you alive?" page for the load balancer. */
    @GetMapping("/ping")
    public String ping() {
        return "pong";
    }
}
