package com.shop.order;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/** An order. The table is called "orders", because ORDER is a reserved word in SQL. */
@Entity
@Table(name = "orders")
public class CustomerOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String customer;

    // TODO (task order_items): one order has many items. Map this list with @OneToMany, pointing at the
    // "order" field of OrderItem (mappedBy), and cascade = CascadeType.ALL so items are saved with it.
    private List<OrderItem> items = new ArrayList<>();

    protected CustomerOrder() {
    }

    public CustomerOrder(String customer) {
        this.customer = customer;
    }

    public Long getId() {
        return id;
    }

    public String getCustomer() {
        return customer;
    }

    public List<OrderItem> getItems() {
        return items;
    }
}
