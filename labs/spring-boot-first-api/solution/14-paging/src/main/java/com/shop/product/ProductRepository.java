package com.shop.product;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query("select p from Product p where p.pricePaise between :min and :max order by p.pricePaise")
    List<Product> inPriceRange(@Param("min") int min, @Param("max") int max);
}
