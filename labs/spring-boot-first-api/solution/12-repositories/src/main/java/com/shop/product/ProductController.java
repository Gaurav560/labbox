package com.shop.product;

import java.net.URI;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/products")
    public List<Product> list(@RequestParam(required = false) String category) {
        return category == null ? repository.findAll() : repository.findByCategoryOrderByNameAsc(category);
    }

    @PostMapping("/products")
    public ResponseEntity<Product> create(@RequestBody NewProduct body) {
        if (repository.existsBySku(body.sku())) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
        Product saved = repository.save(new Product(body.name(), body.pricePaise(), body.category(), body.sku()));
        return ResponseEntity.created(URI.create("/products/" + saved.getId())).body(saved);
    }
}
