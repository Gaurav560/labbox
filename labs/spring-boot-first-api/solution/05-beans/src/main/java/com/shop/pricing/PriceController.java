package com.shop.pricing;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    static final int LASSI_PAISE = 2000;

    private final PriceCalculator calculator;

    public PriceController(PriceCalculator calculator) {
        this.calculator = calculator;
    }

    @GetMapping("/lassi/price")
    public int lassiPrice() {
        return calculator.withGst(LASSI_PAISE);
    }
}
