package com.shop.supplier;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;

@RestController
public class SupplierController {

    private final SupplierClient supplier;

    public SupplierController(SupplierClient supplier) {
        this.supplier = supplier;
    }

    @GetMapping("/supplier-stock/{sku}")
    public ResponseEntity<Map<String, Object>> stock(@PathVariable String sku) {
        try {
            return ResponseEntity.ok(Map.of("sku", sku, "available", supplier.available(sku)));
        } catch (RestClientException e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of("sku", sku, "error", "Supplier unavailable"));
        }
    }
}
