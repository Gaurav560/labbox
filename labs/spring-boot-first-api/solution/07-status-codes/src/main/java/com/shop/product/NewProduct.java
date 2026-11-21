package com.shop.product;

/** What a client sends to create a product. Jackson fills it from the request's JSON. */
public record NewProduct(String name, int pricePaise) {
}
