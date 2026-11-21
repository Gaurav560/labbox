package com.shop.customer;

import java.net.URI;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CustomerController {

    public record Customer(long id, String name, String email, String phone) {
    }

    private final List<Customer> customers = new CopyOnWriteArrayList<>();
    private final AtomicLong nextId = new AtomicLong(1);

    @PostMapping("/customers")
    public ResponseEntity<Customer> create(@Valid @RequestBody NewCustomer body) {
        Customer c = new Customer(nextId.getAndIncrement(), body.name(), body.email(), body.phone());
        customers.add(c);
        return ResponseEntity.created(URI.create("/customers/" + c.id())).body(c);
    }
}
