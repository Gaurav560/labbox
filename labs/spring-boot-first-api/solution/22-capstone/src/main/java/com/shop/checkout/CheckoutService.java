package com.shop.checkout;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CheckoutService {

    private final StockRepository stock;
    private final OrderRepository orders;

    public CheckoutService(StockRepository stock, OrderRepository orders) {
        this.stock = stock;
        this.orders = orders;
    }

    @Transactional
    public ShopOrder checkout(CheckoutRequest request) {
        int total = 0;
        for (CheckoutRequest.Line line : request.items()) {
            StockItem item = stock.findById(line.sku()).orElseThrow(() -> new OutOfStockException(line.sku()));
            item.take(line.quantity());
            total += item.getPricePaise() * line.quantity();
        }
        return orders.save(new ShopOrder(request.customerEmail(), total));
    }
}
