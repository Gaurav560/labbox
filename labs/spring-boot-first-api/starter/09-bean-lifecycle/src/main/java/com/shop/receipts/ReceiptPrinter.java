package com.shop.receipts;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;

/** One customer's receipt: it collects lines while their order is rung up. It keeps state! */
// TODO (task prototype_scope): every customer needs a new, empty receipt. Make Spring create a new
// ReceiptPrinter each time one is asked for, instead of sharing one.
@Component
public class ReceiptPrinter {

    private final List<String> lines = new ArrayList<>();

    public void add(String line) {
        lines.add(line);
    }

    public List<String> lines() {
        return lines;
    }
}
