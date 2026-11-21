package com.shop.cart;

import java.util.ArrayList;
import java.util.List;

import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** The shopping cart (one cart for the whole demo, to keep the chapter about requests). */
@RestController
@RequestMapping("/api/v1")
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

    @DeleteMapping("/cart")
    public List<String> empty() {
        items.clear();
        return items;
    }
}
