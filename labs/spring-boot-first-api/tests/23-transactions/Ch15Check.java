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
            int kulfiBefore = qty("KUL-1");
            Map<String, Integer> items = new LinkedHashMap<>();
            items.put("KUL-1", 2);   // in stock
            items.put("SAM-1", 5);   // only 1 left: fails after the kulfi was taken
            try {
                orders.placeOrder(items);
            } catch (RuntimeException expected) {
                // OutOfStockException
            }
            int kulfiAfter = qty("KUL-1");
            if (kulfiAfter != kulfiBefore) {
                R.fail("place_order_atomic", "The samosas ran out, yet 2 kulfis were still taken off the stock: each save committed on its own. Run placeOrder in one transaction.", "KUL-1: " + kulfiBefore, "KUL-1: " + kulfiAfter);
            } else {
                R.pass("place_order_atomic", "@Transactional: when the samosas ran out, the kulfi that had already been taken went back too. All or nothing.");
            }
        });
    }

    @Test
    void rollbackChecked() {
        R.task("rollback_checked", () -> {
            int custardBefore = qty("CUS-1");
            try {
                orders.placePaidOrder(Map.of("CUS-1", 1), "DECLINE-4242");
            } catch (Exception expected) {
                // PaymentDeclinedException
            }
            int custardAfter = qty("CUS-1");
            if (custardAfter != custardBefore) {
                R.fail("rollback_checked", "The card was declined, but the custard stayed taken: a checked exception commits by default. Add rollbackFor for PaymentDeclinedException.", "CUS-1: " + custardBefore, "CUS-1: " + custardAfter);
            } else {
                R.pass("rollback_checked", "rollbackFor = PaymentDeclinedException.class: a declined card now undoes the whole order, not only unchecked failures.");
            }
        });
    }
}
