package com.shop.visits;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class StatsController {

    private final VisitCounter counter;

    public StatsController(VisitCounter counter) {
        this.counter = counter;
    }

    @GetMapping("/stats")
    public int stats() {
        return counter.count();
    }
}
