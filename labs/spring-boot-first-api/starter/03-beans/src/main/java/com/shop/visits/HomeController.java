package com.shop.visits;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    // TODO (task one_counter): this makes a second VisitCounter of its own. Ask Spring for the shared
    // one in the constructor instead.
    private final VisitCounter counter = new VisitCounter();

    @GetMapping("/")
    public String home() {
        counter.add();
        return "Welcome";
    }
}
