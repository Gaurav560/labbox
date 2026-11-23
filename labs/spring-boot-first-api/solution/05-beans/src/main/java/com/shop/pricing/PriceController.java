package com.shop.pricing;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    static final int KULFI_PAISE = 2000;

    private final PriceCalculator calculator;

    public PriceController(PriceCalculator calculator) {
        this.calculator = calculator;
    }

    @GetMapping("/kulfi/price")
    public int kulfiPrice() {
        return calculator.withGst(KULFI_PAISE);
    }
}
