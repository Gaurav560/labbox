package com.shop.product;

/** Thrown by the service when a product does not exist. */
public class ProductNotFoundException extends RuntimeException {

    private final long id;

    public ProductNotFoundException(long id) {
        super("No product " + id);
        this.id = id;
    }

    public long id() {
        return id;
    }
}
