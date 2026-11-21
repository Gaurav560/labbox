package com.shop.checkout;

public class OutOfStockException extends RuntimeException {

    private final String sku;

    public OutOfStockException(String sku) {
        super("Not enough stock for " + sku);
        this.sku = sku;
    }

    public String sku() {
        return sku;
    }
}
