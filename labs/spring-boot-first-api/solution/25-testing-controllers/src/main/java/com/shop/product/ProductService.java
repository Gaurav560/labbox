package com.shop.product;

import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private final Map<Long, Product> products = Map.of(
            1L, new Product(1, "Masala tea", 2000),
            2L, new Product(2, "Samosa", 1800));

    public Optional<Product> find(long id) {
        return Optional.ofNullable(products.get(id));
    }
}
