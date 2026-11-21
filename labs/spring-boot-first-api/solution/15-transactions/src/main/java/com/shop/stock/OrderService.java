package com.shop.stock;

import java.util.Map;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    private final StockRepository stock;

    public OrderService(StockRepository stock) {
        this.stock = stock;
    }

    /** Takes every item off the stock. If any item runs out, nothing may change. */
    @Transactional
    public void placeOrder(Map<String, Integer> items) {
        for (Map.Entry<String, Integer> e : items.entrySet()) {
            StockItem s = stock.findById(e.getKey()).orElseThrow(() -> new OutOfStockException(e.getKey()));
            s.take(e.getValue());
            stock.saveAndFlush(s);
        }
    }

    /** Takes the items, then charges the card. A declined card must undo the stock changes too. */
    @Transactional(rollbackFor = PaymentDeclinedException.class)
    public void placePaidOrder(Map<String, Integer> items, String card) throws PaymentDeclinedException {
        for (Map.Entry<String, Integer> e : items.entrySet()) {
            StockItem s = stock.findById(e.getKey()).orElseThrow(() -> new OutOfStockException(e.getKey()));
            s.take(e.getValue());
            stock.saveAndFlush(s);
        }
        if (card.startsWith("DECLINE")) {
            throw new PaymentDeclinedException(card);
        }
    }
}
