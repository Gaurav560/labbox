package com.shop.check;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.LinkedHashMap;

import com.shop.stock.OrderService;
import com.shop.stock.StockRepository;

@SpringBootTest
@AutoConfigureMockMvc
class Ch15Check {
    @Autowired
    OrderService orders;
    @Autowired
    StockRepository stock;

    int qty(String sku) {
        return stock.findById(sku).orElseThrow().getQuantity();
    }

    @Test
    void placeOrderAtomic() {
        R.task("place_order_atomic", () -> {
            int teaBefore = qty("TEA-1");
            Map<String, Integer> items = new LinkedHashMap<>();
            items.put("TEA-1", 2);   // in stock
            items.put("SAM-1", 5);   // only 1 left: fails after the tea was taken
            try {
                orders.placeOrder(items);
            } catch (RuntimeException expected) {
                // OutOfStockException
            }
            int teaAfter = qty("TEA-1");
            if (teaAfter != teaBefore) {
                R.fail("place_order_atomic", "The samosas ran out, yet 2 teas were still taken off the stock: each save committed on its own. Run placeOrder in one transaction.", "TEA-1: " + teaBefore, "TEA-1: " + teaAfter);
            } else {
                R.pass("place_order_atomic", "@Transactional: when the samosas ran out, the tea that had already been taken went back too. All or nothing.");
            }
        });
    }

    @Test
    void rollbackChecked() {
        R.task("rollback_checked", () -> {
            int coffeeBefore = qty("COF-1");
            try {
                orders.placePaidOrder(Map.of("COF-1", 1), "DECLINE-4242");
            } catch (Exception expected) {
                // PaymentDeclinedException
            }
            int coffeeAfter = qty("COF-1");
            if (coffeeAfter != coffeeBefore) {
                R.fail("rollback_checked", "The card was declined, but the coffee stayed taken: a checked exception commits by default. Add rollbackFor for PaymentDeclinedException.", "COF-1: " + coffeeBefore, "COF-1: " + coffeeAfter);
            } else {
                R.pass("rollback_checked", "rollbackFor = PaymentDeclinedException.class: a declined card now undoes the whole order, not only unchecked failures.");
            }
        });
    }
}
