package com.shop.stock;

import java.util.Map;

import org.springframework.stereotype.Service;

@Service
public class StockService {

    private final Map<String, Integer> stock = new java.util.concurrent.ConcurrentHashMap<>(Map.of("LAS-1", 10, "SAM-1", 0));

    /** Takes one item off the stock; false when there is none left. */
    public boolean take(String sku) {
        int left = stock.getOrDefault(sku, 0);
        if (left == 0) {
            // TODO (task log_warning): log this with SLF4J at WARN level, as "Out of stock: <sku>",
            // instead of printing it. (A Logger from LoggerFactory.getLogger(StockService.class).)
            System.out.println("out of stock " + sku);
            return false;
        }
        stock.put(sku, left - 1);
        return true;
    }
}
