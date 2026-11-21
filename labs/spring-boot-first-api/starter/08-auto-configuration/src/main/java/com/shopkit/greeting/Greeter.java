package com.shopkit.greeting;

/** Part of "ShopKit", a small library: greets customers with a message. */
public class Greeter {

    private final String message;

    public Greeter(String message) {
        this.message = message;
    }

    public String greet() {
        return message;
    }
}
