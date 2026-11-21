package com.shop.product;

/** A product in the shop. Prices are in paise: 2500 is Rs 25.00. */
public record Product(long id, String name, int pricePaise) {
}
