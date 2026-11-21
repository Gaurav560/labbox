package com.shop.receipts;

import java.util.ArrayList;
import java.util.List;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

/** One customer's receipt: it collects lines while their order is rung up. It keeps state! */
@Component
@Scope("prototype")
public class ReceiptPrinter {

    private final List<String> lines = new ArrayList<>();

    public void add(String line) {
        lines.add(line);
    }

    public List<String> lines() {
        return lines;
    }
}
