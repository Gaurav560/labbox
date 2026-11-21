package com.shop.product;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    // TODO (task paged_products): take a Pageable parameter and return a Page<Product> from
    // repository.findAll(pageable), so ?page=0&size=2&sort=name works.
    @GetMapping("/products")
    public List<Product> all() {
        return repository.findAll();
    }

    // TODO (task price_range): answer with the repository's inPriceRange(min, max).
    @GetMapping("/products/price-range")
    public List<Product> priceRange(@RequestParam int min, @RequestParam int max) {
        return List.of();
    }
}
