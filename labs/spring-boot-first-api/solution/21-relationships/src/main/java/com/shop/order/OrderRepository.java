package com.shop.order;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface OrderRepository extends JpaRepository<CustomerOrder, Long> {

    @Query("select distinct o from CustomerOrder o join fetch o.items")
    List<CustomerOrder> findAllWithItems();
}
