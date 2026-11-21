package com.shop.payments;

import org.springframework.stereotype.Component;

@Component
public class CardGateway implements PaymentGateway {

    @Override
    public String name() {
        return "card";
    }

    @Override
    public String pay(int paise) {
        return "Paid Rs " + paise / 100 + " by card";
    }
}
