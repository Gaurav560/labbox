package com.shop.product;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class ProductController {

    static final int NEW_PRODUCT_COST_PAISE = 0; // the cost is filled in later by the back office

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/products")
    public List<Product> all() {
        return repository.findAll();
    }

    @PostMapping("/products")
    public Product create(@RequestBody NewProduct body) {
        return repository.add(body.name(), body.pricePaise(), NEW_PRODUCT_COST_PAISE);
    }

    @GetMapping("/products/{id}/view")
    public ProductView view(@PathVariable long id) {
        Product p = repository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        String price = String.format("Rs %d.%02d", p.pricePaise() / 100, p.pricePaise() % 100);
        return new ProductView(p.id(), p.name(), price);
    }
}
