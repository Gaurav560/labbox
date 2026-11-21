package com.shop;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MerchantController {

    static final List<String> MERCHANTS = List.of("Kirana King", "Brew Point", "Annapurna Mess");

    @GetMapping("/hello")
    public String hello() {
        return "Hello from the Shop API!";
    }

    @GetMapping("/merchants")
    public List<String> merchants() {
        return MERCHANTS.stream().sorted().toList();
    }
}
