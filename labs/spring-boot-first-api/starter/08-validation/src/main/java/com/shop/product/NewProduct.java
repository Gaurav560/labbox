package com.shop.product;

// TODO (task validate_product): name must not be blank and at most 40 characters; pricePaise must be positive.
public record NewProduct(String name, int pricePaise) {
}
