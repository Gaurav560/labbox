package com.shop.stock;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Places orders over HTTP, so you can watch the stock change (or not) with curl. */
@RestController
public class OrderController {

    private final OrderService orders;

    public OrderController(OrderService orders) {
        this.orders = orders;
    }

    /** POST /orders with a body like {"LAS-1": 2, "SAM-1": 5}. */
    @PostMapping("/orders")
    public ResponseEntity<String> place(@RequestBody Map<String, Integer> items) {
        try {
            orders.placeOrder(items);
            return ResponseEntity.ok("Order placed");
        } catch (OutOfStockException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(e.getMessage());
        }
    }

    /** POST /paid-orders?card=4111 with the same body. A card starting with DECLINE is declined. */
    @PostMapping("/paid-orders")
    public ResponseEntity<String> placePaid(@RequestBody Map<String, Integer> items, @RequestParam String card) {
        try {
            orders.placePaidOrder(items, card);
            return ResponseEntity.ok("Order placed and paid");
        } catch (OutOfStockException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(e.getMessage());
        } catch (PaymentDeclinedException e) {
            return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED).body(e.getMessage());
        }
    }
}
