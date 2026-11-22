package com.shop.checkout;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Positive;

/** POST /checkout: {"customerEmail": "asha@shop.in", "items": [{"sku": "LAS-1", "quantity": 2}]} */
public record CheckoutRequest(@NotBlank @Email String customerEmail, @NotEmpty List<@Valid Line> items) {

    public record Line(@NotBlank String sku, @Positive int quantity) {
    }
}
