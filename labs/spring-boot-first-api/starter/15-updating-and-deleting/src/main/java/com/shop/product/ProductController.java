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

    // TODO (task put_product): PUT /products/{id} replaces the whole product with the ProductInput in the body
    // (the id stays the one from the path), and answers 200 with the new product, or 404 if there is none.

    // TODO (task patch_price): PATCH /products/{id} changes only the fields present in the ProductPatch body
    // (a null field means "keep the old value"), and answers 200 with the result, or 404 if there is none.
}
