package com.shop.pricing;

// TODO (task price_service): make this class a bean, so Spring creates one and can inject it.
public class PriceCalculator {

    /** A price in paise, with 18% GST added. */
    public int withGst(int paise) {
        return paise + paise * 18 / 100;
    }
}
