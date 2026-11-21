package com.shop.checkout;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "orders")
public class ShopOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String customerEmail;

    private int totalPaise;

    protected ShopOrder() {
    }

    public ShopOrder(String customerEmail, int totalPaise) {
        this.customerEmail = customerEmail;
        this.totalPaise = totalPaise;
    }

    public Long getId() {
        return id;
    }

    public String getCustomerEmail() {
        return customerEmail;
    }

    public int getTotalPaise() {
        return totalPaise;
    }
}
