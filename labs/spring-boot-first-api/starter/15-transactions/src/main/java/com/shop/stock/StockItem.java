package com.shop.stock;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class StockItem {

    @Id
    private String sku;

    private int quantity;

    protected StockItem() {
    }

    public StockItem(String sku, int quantity) {
        this.sku = sku;
        this.quantity = quantity;
    }

    public String getSku() {
        return sku;
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
