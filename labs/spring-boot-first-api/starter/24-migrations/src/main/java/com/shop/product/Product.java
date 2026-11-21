package com.shop.product;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    private int pricePaise;

    @Column(nullable = false)
    private String category;

    @Column(nullable = false, unique = true)
    private String sku;

    protected Product() {
    }

    public Product(String name, int pricePaise, String category, String sku) {
        this.name = name;
        this.pricePaise = pricePaise;
        this.category = category;
        this.sku = sku;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public int getPricePaise() {
        return pricePaise;
    }

    public String getCategory() {
        return category;
    }

    public String getSku() {
        return sku;
    }
}
