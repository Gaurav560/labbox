package com.shop.checkout;

import org.springframework.stereotype.Service;

@Service
public class CheckoutService {

    private final StockRepository stock;
    private final OrderRepository orders;

    public CheckoutService(StockRepository stock, OrderRepository orders) {
        this.stock = stock;
        this.orders = orders;
    }

    // TODO (task checkout): in ONE transaction, for each line: find the StockItem (an unknown sku is out of
    // stock), take the quantity, and add price x quantity to the total. Then save a ShopOrder with the
    // email and the total, and return it. If any line is out of stock, nothing may change.
    public ShopOrder checkout(CheckoutRequest request) {
        throw new UnsupportedOperationException("not written yet");
    }
}
