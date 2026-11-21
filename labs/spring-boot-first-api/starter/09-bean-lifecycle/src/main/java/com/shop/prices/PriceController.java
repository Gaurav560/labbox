package com.shop.prices;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    private final PriceCatalog catalog;

    public PriceController(PriceCatalog catalog) {
        this.catalog = catalog;
    }

    @GetMapping("/prices/count")
    public int count() {
        return catalog.count();
    }

    @GetMapping("/prices/{sku}")
    public ResponseEntity<Integer> price(@PathVariable String sku) {
        return catalog.price(sku).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }
}
