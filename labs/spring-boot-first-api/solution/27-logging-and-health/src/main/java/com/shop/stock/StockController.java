package com.shop.stock;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

/** Takes one item off the stock over HTTP, so you can trigger the warning with curl. */
@RestController
public class StockController {

    private final StockService stock;

    public StockController(StockService stock) {
        this.stock = stock;
    }

    @PostMapping("/stock/{sku}/take")
    public ResponseEntity<String> take(@PathVariable String sku) {
        return stock.take(sku)
                ? ResponseEntity.ok("Taken one " + sku)
                : ResponseEntity.status(HttpStatus.CONFLICT).body("Out of stock: " + sku);
    }
}
