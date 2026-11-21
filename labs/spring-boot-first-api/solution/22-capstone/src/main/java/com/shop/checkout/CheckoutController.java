package com.shop.checkout;

import java.net.URI;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CheckoutController {

    private final CheckoutService service;
    private final OrderRepository orders;

    public CheckoutController(CheckoutService service, OrderRepository orders) {
        this.service = service;
        this.orders = orders;
    }

    @PostMapping("/checkout")
    public ResponseEntity<ShopOrder> checkout(@Valid @RequestBody CheckoutRequest request) {
        ShopOrder order = service.checkout(request);
        return ResponseEntity.created(URI.create("/orders/" + order.getId())).body(order);
    }

    @GetMapping("/orders/{id}")
    public ResponseEntity<ShopOrder> order(@PathVariable long id) {
        return orders.findById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }
}
