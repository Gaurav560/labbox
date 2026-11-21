package com.shop.product;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface ProductRepository extends JpaRepository<Product, Long> {

    // The planted bug: the right products, the wrong order.
    @Query("select p from Product p where p.category = ?1 order by p.name desc")
    List<Product> findByCategoryOrderByNameAsc(String category);
}
