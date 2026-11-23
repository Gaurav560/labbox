package com.shop;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

/**
 * A small, finished API for chapter 1: you do not change this file, you explore it with curl.
 * (You will learn to write every line of it in the chapters that follow.)
 */
@RestController
public class MenuController {

    /** A new item from the client: the server picks the id. */
    public record NewItem(String name, int pricePaise) {
    }

    private final List<MenuItem> menu = new ArrayList<>(List.of(
            new MenuItem(1, "Mango kulfi", 2000),
            new MenuItem(2, "Samosa", 1800),
            new MenuItem(3, "Fruit custard", 3000)));

    @GetMapping("/hello")
    public String hello() {
        return "Hello! This is the canteen menu API.";
    }

    @GetMapping("/menu")
    public List<MenuItem> all() {
        return menu;
    }

    @GetMapping("/menu/{id}")
    public ResponseEntity<MenuItem> one(@PathVariable long id) {
        return menu.stream().filter(m -> m.id() == id).findFirst()
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/menu")
    public ResponseEntity<MenuItem> add(@RequestBody NewItem item) {
        long id = menu.stream().mapToLong(MenuItem::id).max().orElse(0) + 1;
        MenuItem created = new MenuItem(id, item.name(), item.pricePaise());
        menu.add(created);
        return ResponseEntity.created(URI.create("/menu/" + id)).body(created);
    }

    @DeleteMapping("/menu/{id}")
    public ResponseEntity<Void> remove(@PathVariable long id) {
        return menu.removeIf(m -> m.id() == id) ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }
}
