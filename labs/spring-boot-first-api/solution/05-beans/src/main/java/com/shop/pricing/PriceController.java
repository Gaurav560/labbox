package com.shop.pricing;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    static final int TEA_PAISE = 2000;

    private final PriceCalculator calculator;

    public PriceController(PriceCalculator calculator) {
        this.calculator = calculator;
    }

    @GetMapping("/tea/price")
    public int teaPrice() {
        return calculator.withGst(TEA_PAISE);
    }
}
