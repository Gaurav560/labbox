package com.shop.pricing;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    static final int LASSI_PAISE = 2000;

    private PriceCalculator calculator;

    // TODO (task price_service): add a constructor that takes a PriceCalculator, and keep it in the field.

    @GetMapping("/lassi/price")
    public int lassiPrice() {
        return calculator == null ? 0 : calculator.withGst(LASSI_PAISE);
    }
}
