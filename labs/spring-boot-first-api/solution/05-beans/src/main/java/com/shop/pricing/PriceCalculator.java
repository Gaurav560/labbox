package com.shop.pricing;

import org.springframework.stereotype.Service;

@Service
public class PriceCalculator {

    /** A price in paise, with 18% GST added. */
    public int withGst(int paise) {
        return paise + paise * 18 / 100;
    }
}
