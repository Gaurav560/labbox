package com.shop.order;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    public record OrderSummary(long id, String customer, int items, int totalPaise) {
    }

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public OrderSummary summary(long id) {
        return repository.findById(id).map(OrderService::toSummary).orElse(null);
    }

    @Transactional(readOnly = true)
    public List<OrderSummary> summaries() {
        return repository.findAll().stream().map(OrderService::toSummary).toList();
    }

    static OrderSummary toSummary(CustomerOrder o) {
        int total = o.getItems().stream().mapToInt(i -> i.getPricePaise() * i.getQuantity()).sum();
        return new OrderSummary(o.getId(), o.getCustomer(), o.getItems().size(), total);
    }
}
