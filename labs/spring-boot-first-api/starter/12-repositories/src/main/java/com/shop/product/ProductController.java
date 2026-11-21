package com.shop.product;

import java.net.URI;
import java.util.List;

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

    // TODO (task find_by_category): when a category is given, answer only that category, using the
    // repository's derived query (not a filter here in Java).
    @GetMapping("/products")
    public List<Product> list(@RequestParam(required = false) String category) {
        return repository.findAll();
    }

    // TODO (task sku_conflict): answer 409 Conflict, without saving, when the sku already exists.
    @PostMapping("/products")
    public ResponseEntity<Product> create(@RequestBody NewProduct body) {
        Product saved = repository.save(new Product(body.name(), body.pricePaise(), body.category(), body.sku()));
        return ResponseEntity.created(URI.create("/products/" + saved.getId())).body(saved);
    }
}
