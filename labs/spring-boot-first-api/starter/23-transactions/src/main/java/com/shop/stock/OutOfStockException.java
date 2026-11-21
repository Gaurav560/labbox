package com.shop.stock;

public class OutOfStockException extends RuntimeException {

    public OutOfStockException(String sku) {
        super("Not enough stock for " + sku);
    }
}
