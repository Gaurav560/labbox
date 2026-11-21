package com.shop;

/** One thing on the canteen menu. Prices are in paise (2000 paise = Rs 20), so there are no rounding errors. */
public record MenuItem(long id, String name, int pricePaise) {
}
