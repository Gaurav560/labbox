package com.shop;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ShopController {

    @GetMapping("/products")
    public List<String> products() {
        return List.of("Mango kulfi", "Samosa");
    }

    @GetMapping("/admin/report")
    public String report() {
        return "Sales today: 42 orders";
    }

    @DeleteMapping("/products/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        return ResponseEntity.noContent().build();
    }
}
