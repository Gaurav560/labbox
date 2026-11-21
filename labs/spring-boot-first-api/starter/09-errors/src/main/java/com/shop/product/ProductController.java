package com.shop.product;

import java.net.URI;
import java.util.List;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping("/products")
    public List<Product> all() {
        return service.all();
    }

    @GetMapping("/products/{id}")
    public Product get(@PathVariable long id) {
        return service.get(id);
    }

    @PostMapping("/products")
    public ResponseEntity<Product> create(@Valid @RequestBody NewProduct body) {
        Product p = service.create(body);
        return ResponseEntity.created(URI.create("/products/" + p.id())).body(p);
    }
}
