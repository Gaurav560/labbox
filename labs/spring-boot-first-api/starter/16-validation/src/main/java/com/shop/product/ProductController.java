package com.shop.product;

import java.net.URI;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/products")
    public List<Product> all() {
        return repository.findAll();
    }

    // TODO (task validate_product): validate the body before this method runs.
    @PostMapping("/products")
    public ResponseEntity<Product> create(@RequestBody NewProduct body) {
        Product p = repository.add(body.name(), body.pricePaise(), 0);
        return ResponseEntity.created(URI.create("/products/" + p.id())).body(p);
    }

    @DeleteMapping("/products/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        return repository.delete(id) ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }
}
