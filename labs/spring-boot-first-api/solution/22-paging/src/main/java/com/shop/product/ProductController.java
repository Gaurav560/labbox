package com.shop.product;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/products")
    public Page<Product> all(Pageable pageable) {
        return repository.findAll(pageable);
    }

    @GetMapping("/products/price-range")
    public List<Product> priceRange(@RequestParam int min, @RequestParam int max) {
        return repository.inPriceRange(min, max);
    }
}
