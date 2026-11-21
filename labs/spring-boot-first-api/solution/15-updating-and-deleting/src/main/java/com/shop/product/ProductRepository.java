package com.shop.product;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.TreeMap;

import org.springframework.stereotype.Repository;

/** Products kept in memory, by id. (A real database arrives in chapter 19.) */
@Repository
public class ProductRepository {

    private final Map<Long, Product> products = new ConcurrentHashMap<>(Map.of(
            1L, new Product(1, "Masala tea", 2000, 40),
            2L, new Product(2, "Filter coffee", 3000, 25),
            3L, new Product(3, "Samosa", 1800, 60)));

    public List<Product> findAll() {
        return List.copyOf(new TreeMap<>(products).values());
    }

    public Optional<Product> findById(long id) {
        return Optional.ofNullable(products.get(id));
    }

    /** Stores the product under its id, replacing what was there. */
    public Product save(Product product) {
        products.put(product.id(), product);
        return product;
    }

    public boolean delete(long id) {
        return products.remove(id) != null;
    }
}
