package com.shop.product;

import org.springframework.data.jpa.repository.JpaRepository;

/** Spring Data writes the implementation: findAll, findById, save, delete, count and more. */
public interface ProductRepository extends JpaRepository<Product, Long> {
}
