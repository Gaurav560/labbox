package com.shop.stock;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class StockController {

    private final StockRepository stock;

    public StockController(StockRepository stock) {
        this.stock = stock;
    }

    @GetMapping("/stock/{sku}")
    public Map<String, Object> one(@PathVariable String sku) {
        return stock.findById(sku).<Map<String, Object>>map(s -> Map.of("sku", s.getSku(), "quantity", s.getQuantity()))
                .orElse(Map.of("sku", sku, "quantity", 0));
    }
}
