package com.shop.product;

/** A product in the shop: its name, its price in paise, and how many are in stock. */
public record Product(long id, String name, int pricePaise, int stock) {
}
