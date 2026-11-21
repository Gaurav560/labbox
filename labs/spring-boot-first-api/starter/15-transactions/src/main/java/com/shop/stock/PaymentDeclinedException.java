package com.shop.stock;

/** A checked exception: the card was declined. */
public class PaymentDeclinedException extends Exception {

    public PaymentDeclinedException(String card) {
        super("Card " + card + " was declined");
    }
}
