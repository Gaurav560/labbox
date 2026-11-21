package com.shop.payments;

import org.springframework.stereotype.Service;

/** Takes payment for an order, with the shop's main payment gateway. */
@Service
public class CheckoutService {

    private final PaymentGateway gateway;

    public CheckoutService(PaymentGateway gateway) {
        this.gateway = gateway;
    }

    public String checkout(int paise) {
        return gateway.pay(paise);
    }
}
