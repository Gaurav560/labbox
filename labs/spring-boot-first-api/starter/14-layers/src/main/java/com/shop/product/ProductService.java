package com.shop.product;

import java.util.List;

import org.springframework.stereotype.Service;

/** The service layer: the shop's rules. Controllers call it; it calls the repository. */
@Service
public class ProductService {

    static final int BUDGET_PAISE = 5000;

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<Product> all() {
        return repository.findAll();
    }

    /** The average price in paise. */
    public int averagePrice() {
        // TODO (task thin_controller): work out the average here, from the repository's products.
        return 0;
    }

    /** Products under Rs 50. */
    public List<Product> budgetProducts() {
        // TODO (task budget_products): ask the repository for the products cheaper than BUDGET_PAISE.
        return List.of();
    }
}
