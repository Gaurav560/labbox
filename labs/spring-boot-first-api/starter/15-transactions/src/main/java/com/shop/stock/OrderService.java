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
    // TODO (task place_order_atomic): make this method run in one transaction.
    public void placeOrder(Map<String, Integer> items) {
        for (Map.Entry<String, Integer> e : items.entrySet()) {
            StockItem s = stock.findById(e.getKey()).orElseThrow(() -> new OutOfStockException(e.getKey()));
            s.take(e.getValue());
            stock.saveAndFlush(s);
        }
    }

    /** Takes the items, then charges the card. A declined card must undo the stock changes too. */
    // TODO (task rollback_checked): this is transactional, but a checked exception does not roll back by
    // default. Make PaymentDeclinedException roll the transaction back too.
    @Transactional
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
