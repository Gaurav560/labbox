package com.shop.product;

/** What clients see of a product: no internal cost. price is formatted, for example "Rs 20.00". */
public record ProductView(long id, String name, String price) {
}
