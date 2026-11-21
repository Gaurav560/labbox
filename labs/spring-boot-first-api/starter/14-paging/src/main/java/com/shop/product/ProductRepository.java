package com.shop.product;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, Long> {

    // TODO (task price_range): a @Query in JPQL: the products whose price is between min and max
    // (both included), cheapest first. Name the method inPriceRange(int min, int max).
}
