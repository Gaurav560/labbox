package com.shop.product;

/** A product as the shop stores it. costPaise is what the shop paid: internal, never sent to clients. */
public record Product(long id, String name, int pricePaise, int costPaise) {
}
