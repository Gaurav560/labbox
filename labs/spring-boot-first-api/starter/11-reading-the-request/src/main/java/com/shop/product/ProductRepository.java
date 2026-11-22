package com.shop.product;

import java.util.List;

import org.springframework.stereotype.Repository;

@Repository
public class ProductRepository {

    private static final List<Product> PRODUCTS = List.of(
            new Product(1, "Mango lassi", 2000),
            new Product(2, "Filter coffee", 3000),
            new Product(3, "Samosa", 1800),
            new Product(4, "Paneer roll", 9000));

    public List<Product> findAll() {
        return PRODUCTS;
    }
}
