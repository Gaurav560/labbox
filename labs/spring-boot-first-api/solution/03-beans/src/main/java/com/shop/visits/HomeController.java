package com.shop.visits;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    private final VisitCounter counter;

    public HomeController(VisitCounter counter) {
        this.counter = counter;
    }

    @GetMapping("/")
    public String home() {
        counter.add();
        return "Welcome";
    }
}
