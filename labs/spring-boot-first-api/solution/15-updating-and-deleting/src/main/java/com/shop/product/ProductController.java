package com.shop.product;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/products")
public class ProductController {

    private final ProductRepository products;

    public ProductController(ProductRepository products) {
        this.products = products;
    }

    @GetMapping
    public List<Product> all() {
        return products.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> one(@PathVariable long id) {
        return ResponseEntity.of(products.findById(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        return products.delete(id) ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> replace(@PathVariable long id, @RequestBody ProductInput in) {
        if (products.findById(id).isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(products.save(new Product(id, in.name(), in.pricePaise(), in.stock())));
    }

    @PatchMapping("/{id}")
    public ResponseEntity<Product> patch(@PathVariable long id, @RequestBody ProductPatch patch) {
        return products.findById(id).map(old -> {
            Product updated = new Product(id,
                    patch.name() != null ? patch.name() : old.name(),
                    patch.pricePaise() != null ? patch.pricePaise() : old.pricePaise(),
                    patch.stock() != null ? patch.stock() : old.stock());
            return ResponseEntity.ok(products.save(updated));
        }).orElse(ResponseEntity.notFound().build());
    }
}
