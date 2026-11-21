package com.shop.product;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

public record NewProduct(@NotBlank @Size(max = 40) String name, @Positive int pricePaise) {
}
