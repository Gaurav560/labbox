package com.shop.receipts;

import java.util.List;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ReceiptController {

    private final ObjectProvider<ReceiptPrinter> receipts;

    // ObjectProvider: ask Spring for a ReceiptPrinter each time one is needed, not once at start-up.
    public ReceiptController(ObjectProvider<ReceiptPrinter> receipts) {
        this.receipts = receipts;
    }

    /** One customer buys one item: their receipt should show just that item. */
    @GetMapping("/receipt/{item}")
    public List<String> receipt(@PathVariable String item) {
        ReceiptPrinter receipt = receipts.getObject();
        receipt.add("1 x " + item);
        return receipt.lines();
    }
}
