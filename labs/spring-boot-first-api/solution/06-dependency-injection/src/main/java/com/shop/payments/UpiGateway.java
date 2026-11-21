package com.shop.payments;

import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;

@Component
@Primary
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
