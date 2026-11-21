package com.shop.product;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Repository;

/** The data layer: where products are kept. Here, a fixed list in memory; a database in chapter 19. */
@Repository
public class ProductRepository {

    private static final List<Product> PRODUCTS = List.of(
            new Product(1, "Masala tea", 2000),
            new Product(2, "Filter coffee", 3000),
            new Product(3, "Samosa", 1800),
            new Product(4, "Paneer roll", 9000));

    public List<Product> findAll() {
        return PRODUCTS;
    }

    public Optional<Product> findById(long id) {
        return PRODUCTS.stream().filter(p -> p.id() == id).findFirst();
    }

    // TODO (task budget_products): add findCheaperThan(int paise): the products whose price is below it.
}
