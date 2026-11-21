package com.shop.checkout;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CheckoutController {

    private final CheckoutService service;
    private final OrderRepository orders;

    public CheckoutController(CheckoutService service, OrderRepository orders) {
        this.service = service;
        this.orders = orders;
    }

    // TODO (task checkout): POST /checkout validates the CheckoutRequest body, calls the service, and answers
    // 201 Created with a Location header /orders/{id} and the order as the body.

    @GetMapping("/orders/{id}")
    public ResponseEntity<ShopOrder> order(@PathVariable long id) {
        return orders.findById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }
}
