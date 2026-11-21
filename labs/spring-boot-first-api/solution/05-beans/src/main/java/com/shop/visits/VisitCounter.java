package com.shop.visits;

import java.util.concurrent.atomic.AtomicInteger;

import org.springframework.stereotype.Component;

@Component
public class VisitCounter {

    private final AtomicInteger count = new AtomicInteger();

    public int add() {
        return count.incrementAndGet();
    }

    public int count() {
        return count.get();
    }
}
