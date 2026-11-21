package com.shop.payments;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CheckoutController {

    private final CheckoutService checkout;

    public CheckoutController(CheckoutService checkout) {
        this.checkout = checkout;
    }

    /** GET /pay/5000 pays Rs 50 with the main gateway. */
    @GetMapping("/pay/{paise}")
    public String pay(@PathVariable int paise) {
        return checkout.checkout(paise);
    }
}
