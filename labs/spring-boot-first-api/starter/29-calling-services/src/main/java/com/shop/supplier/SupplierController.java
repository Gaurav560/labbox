package com.shop.supplier;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SupplierController {

    private final SupplierClient supplier;

    public SupplierController(SupplierClient supplier) {
        this.supplier = supplier;
    }

    // TODO (task handle_supplier_errors): when the supplier fails or is too slow (a RestClientException),
    // answer 503 Service Unavailable instead of 500.
    @GetMapping("/supplier-stock/{sku}")
    public ResponseEntity<Map<String, Object>> stock(@PathVariable String sku) {
        return ResponseEntity.ok(Map.of("sku", sku, "available", supplier.available(sku)));
    }
}
