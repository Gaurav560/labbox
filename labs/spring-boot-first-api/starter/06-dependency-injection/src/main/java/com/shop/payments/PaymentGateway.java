package com.shop.payments;

/** Something that can take a payment. The shop does not care how: card, UPI, wallet... */
public interface PaymentGateway {

    /** A short name, like "card" or "upi". */
    String name();

    /** Takes the payment and returns a receipt line for the customer. */
    String pay(int paise);
}
