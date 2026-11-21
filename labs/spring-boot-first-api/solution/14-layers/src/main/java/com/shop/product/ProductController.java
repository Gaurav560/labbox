package com.shop.product;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** The web layer: turns HTTP requests into calls to the service. */
@RestController
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping("/products")
    public List<Product> products() {
        return service.all();
    }

    @GetMapping("/products/average-price")
    public int averagePrice() {
        return service.averagePrice();
    }

    @GetMapping("/products/budget")
    public List<Product> budget() {
        return service.budgetProducts();
    }
}
