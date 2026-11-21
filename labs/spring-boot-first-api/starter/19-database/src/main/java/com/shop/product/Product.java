package com.shop.product;

// TODO (task product_entity): make this a JPA entity. Put @Entity on the class, and @Id plus
// @GeneratedValue(strategy = GenerationType.IDENTITY) on id. JPA also needs a constructor with no
// arguments; it can be protected.
public class Product {

    private Long id;

    private String name;

    private int pricePaise;

    // TODO (task unique_sku): the database must refuse two products with the same sku, and a missing one.
    private String sku;

    public Product(String name, int pricePaise, String sku) {
        this.name = name;
        this.pricePaise = pricePaise;
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

    public String getSku() {
        return sku;
    }
}
