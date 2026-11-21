package com.shop.product;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, Long> {

    // TODO (task find_by_category): a derived query: the products of one category, sorted by name.

    // TODO (task sku_conflict): a derived query that answers whether a product with this sku exists.
}
