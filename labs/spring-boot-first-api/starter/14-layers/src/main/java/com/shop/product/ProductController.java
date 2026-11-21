package com.shop.product;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** The web layer: turns HTTP requests into calls to the service. */
@RestController
public class ProductController {

    private final ProductService service;
    private final ProductRepository repository;

    public ProductController(ProductService service, ProductRepository repository) {
        this.service = service;
        this.repository = repository;
    }

    @GetMapping("/products")
    public List<Product> products() {
        return service.all();
    }

    // TODO (task thin_controller): this works, but the controller does the service's job and reads the
    // repository itself. Move the calculation into ProductService.averagePrice() and call that here.
    @GetMapping("/products/average-price")
    public int averagePrice() {
        List<Product> products = repository.findAll();
        int total = 0;
        for (Product p : products) {
            total += p.pricePaise();
        }
        return products.isEmpty() ? 0 : total / products.size();
    }

    @GetMapping("/products/budget")
    public List<Product> budget() {
        return service.budgetProducts();
    }
}
