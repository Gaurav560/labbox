package com.shop.product;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
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

    // TODO (task product_by_id): GET /products/{id} returns that product, and 404 for an unknown id.

    // TODO (task search_products): GET /products/search with two optional query parameters:
    //   maxPrice (paise): only products cheaper than or equal to it; no limit when it is missing
    //   sort: "name" (the default) or "price", lowest first
}
