package com.shop.product;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
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

    // TODO (task create_product): POST /products reads a NewProduct from the JSON body, stores it with
    // repository.add(...), and returns the stored Product.

    // TODO (task product_view): GET /products/{id}/view returns a ProductView (id, name, price as "Rs 20.00"),
    // never the internal cost. Unknown id: 404.
    @GetMapping("/products/{id}/view")
    public Product view(@PathVariable long id) {
        return repository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }
}
