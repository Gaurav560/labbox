package com.shop.product;

import java.util.Comparator;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

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

    @GetMapping("/products/{id}")
    public Product byId(@PathVariable long id) {
        return repository.findAll().stream()
                .filter(p -> p.id() == id)
                .findFirst()
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No product " + id));
    }

    @GetMapping("/products/search")
    public List<Product> search(@RequestParam(required = false) Integer maxPrice,
                                @RequestParam(defaultValue = "name") String sort) {
        Comparator<Product> order = sort.equals("price")
                ? Comparator.comparingInt(Product::pricePaise)
                : Comparator.comparing(Product::name);
        return repository.findAll().stream()
                .filter(p -> maxPrice == null || p.pricePaise() <= maxPrice)
                .sorted(order)
                .toList();
    }
}
