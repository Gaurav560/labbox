package com.shop.customer;

// TODO (task validate_customer): name must not be blank, email must be an email address, and phone must
// be exactly 10 digits (a regular expression: [0-9]{10}).
public record NewCustomer(String name, String email, String phone) {
}
