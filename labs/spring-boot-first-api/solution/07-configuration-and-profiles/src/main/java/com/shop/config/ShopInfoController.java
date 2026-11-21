package com.shop.config;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ShopInfoController {

    private final ShopProperties shop;

    public ShopInfoController(ShopProperties shop) {
        this.shop = shop;
    }

    @GetMapping("/shop/info")
    public Map<String, Object> info() {
        return Map.of("name", shop.name(), "freeDeliveryAbovePaise", shop.freeDeliveryAbovePaise());
    }
}
