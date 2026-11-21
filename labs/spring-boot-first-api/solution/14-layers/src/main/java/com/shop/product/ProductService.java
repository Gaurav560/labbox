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
        List<Product> products = repository.findAll();
        if (products.isEmpty()) {
            return 0;
        }
        int total = 0;
        for (Product p : products) {
            total += p.pricePaise();
        }
        return total / products.size();
    }

    /** Products under Rs 50. */
    public List<Product> budgetProducts() {
        return repository.findCheaperThan(BUDGET_PAISE);
    }
}
