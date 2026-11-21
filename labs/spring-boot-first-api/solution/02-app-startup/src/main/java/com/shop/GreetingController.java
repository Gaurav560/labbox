package com.shop;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {

    // Spring fills this from application.properties when it creates the controller.
    @Value("${shop.greeting:not set}")
    private String greeting;

    @GetMapping("/greeting")
    public String greeting() {
        return greeting;
    }
}
