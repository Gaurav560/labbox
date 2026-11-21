package com.shop.product;

/** The body of a PUT: a complete product, every field. (The id comes from the path, never the body.) */
public record ProductInput(String name, int pricePaise, int stock) {
}
