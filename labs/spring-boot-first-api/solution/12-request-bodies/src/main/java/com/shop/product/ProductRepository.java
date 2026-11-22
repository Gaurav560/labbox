package com.shop.product;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Repository;

@Repository
public class ProductRepository {

    private final List<Product> products = new ArrayList<>(List.of(
            new Product(1, "Mango lassi", 2000, 900),
            new Product(2, "Filter coffee", 3000, 1400),
            new Product(3, "Samosa", 1800, 700)));
    private final AtomicLong nextId = new AtomicLong(4);

    public synchronized List<Product> findAll() {
        return List.copyOf(products);
    }

    public synchronized Optional<Product> findById(long id) {
        return products.stream().filter(p -> p.id() == id).findFirst();
    }

    /** Stores a new product with the next free id, and returns it. */
    public synchronized Product add(String name, int pricePaise, int costPaise) {
        Product p = new Product(nextId.getAndIncrement(), name, pricePaise, costPaise);
        products.add(p);
        return p;
    }

    public synchronized boolean delete(long id) {
        return products.removeIf(p -> p.id() == id);
    }
}
