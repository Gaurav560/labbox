package com.shop.stock;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class StockService {

    private static final Logger log = LoggerFactory.getLogger(StockService.class);

    private final Map<String, Integer> stock = new java.util.concurrent.ConcurrentHashMap<>(Map.of("TEA-1", 10, "SAM-1", 0));

    /** Takes one item off the stock; false when there is none left. */
    public boolean take(String sku) {
        int left = stock.getOrDefault(sku, 0);
        if (left == 0) {
            log.warn("Out of stock: {}", sku);
            return false;
        }
        stock.put(sku, left - 1);
        return true;
    }
}
