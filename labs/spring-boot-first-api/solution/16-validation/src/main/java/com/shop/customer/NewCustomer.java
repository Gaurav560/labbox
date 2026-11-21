package com.shop.customer;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record NewCustomer(@NotBlank String name, @NotBlank @Email String email, @Pattern(regexp = "[0-9]{10}") String phone) {
}
