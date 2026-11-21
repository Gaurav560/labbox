package com.shop.checkout;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class StockItem {

    @Id
    private String sku;

    private String name;

    private int pricePaise;

    private int quantity;

    protected StockItem() {
    }

    public String getSku() {
        return sku;
    }

    public String getName() {
        return name;
    }

    public int getPricePaise() {
        return pricePaise;
    }

    public int getQuantity() {
        return quantity;
    }

    public void take(int n) {
        if (n > quantity) {
            throw new OutOfStockException(sku);
        }
        quantity -= n;
    }
}
