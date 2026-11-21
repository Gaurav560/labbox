package com.shop.order;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<CustomerOrder, Long> {

    // TODO (task fix_n_plus_one): add a query that loads every order with its items in one SELECT
    // (JOIN FETCH), and use it in OrderService.summaries().
}
