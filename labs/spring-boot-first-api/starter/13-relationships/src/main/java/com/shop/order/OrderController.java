package com.shop.order;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OrderController {

    private final OrderService service;

    public OrderController(OrderService service) {
        this.service = service;
    }

    @GetMapping("/orders")
    public List<OrderService.OrderSummary> all() {
        return service.summaries();
    }

    @GetMapping("/orders/{id}")
    public ResponseEntity<OrderService.OrderSummary> one(@PathVariable long id) {
        OrderService.OrderSummary s = service.summary(id);
        return s == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(s);
    }
}
