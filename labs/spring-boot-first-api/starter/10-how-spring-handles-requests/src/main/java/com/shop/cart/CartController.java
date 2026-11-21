package com.shop.cart;

import java.util.ArrayList;
import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

/** The shopping cart (one cart for the whole demo, to keep the chapter about requests). */
// TODO (task class_prefix): version 1 of the API lives under /api/v1: give the whole class that prefix,
// once, so every path below starts with /api/v1 (for example GET /api/v1/cart).
@RestController
public class CartController {

    private final List<String> items = new ArrayList<>();

    @GetMapping("/cart")
    public List<String> cart() {
        return items;
    }

    @PostMapping("/cart/items/{item}")
    public List<String> add(@PathVariable String item) {
        items.add(item);
        return items;
    }

    // TODO (task method_routing): DELETE on the cart's own path (the same path as GET above) empties the
    // cart and returns it (now empty).
}
