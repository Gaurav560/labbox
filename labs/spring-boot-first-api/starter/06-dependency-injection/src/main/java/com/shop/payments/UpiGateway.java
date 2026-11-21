package com.shop.payments;

import org.springframework.stereotype.Component;

// TODO (task primary_gateway): two beans now fit PaymentGateway, so Spring cannot choose one for
// CheckoutService and the app does not start. UPI is the shop's main gateway: mark this bean as the
// one to use when there is a choice.
@Component
public class UpiGateway implements PaymentGateway {

    @Override
    public String name() {
        return "upi";
    }

    @Override
    public String pay(int paise) {
        return "Paid Rs " + paise / 100 + " by UPI";
    }
}
