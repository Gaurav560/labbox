package com.shop.product;

import java.util.List;

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

    // TODO (task created_201): answer 201 Created, with a Location header /products/{new id}, and the product.
    @PostMapping("/products")
    public Product create(@RequestBody NewProduct body) {
        return repository.add(body.name(), body.pricePaise(), 0);
    }

    // TODO (task delete_204): answer 204 No Content when the product was deleted, 404 when there was none.
    @DeleteMapping("/products/{id}")
    public void delete(@PathVariable long id) {
        repository.delete(id);
    }
}
