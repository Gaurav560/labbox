package com.shop.config;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ShopInfoController {

    // TODO (task shop_properties): receive ShopProperties in the constructor, and answer with its values.
    @GetMapping("/shop/info")
    public Map<String, Object> info() {
        return Map.of("name", "unknown", "freeDeliveryAbovePaise", 0);
    }
}
