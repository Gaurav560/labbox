package com.shop.order;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class OrderItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String product;

    private int quantity;

    private int pricePaise;

    // TODO (task order_items): many items belong to one order. Map this field with @ManyToOne; its foreign
    // key column is order_id.
    private CustomerOrder order;

    protected OrderItem() {
    }

    public String getProduct() {
        return product;
    }

    public int getQuantity() {
        return quantity;
    }

    public int getPricePaise() {
        return pricePaise;
    }
}
