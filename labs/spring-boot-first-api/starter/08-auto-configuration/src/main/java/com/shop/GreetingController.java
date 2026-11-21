package com.shop;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.shopkit.greeting.FestivalBanner;
import com.shopkit.greeting.Greeter;

@RestController
public class GreetingController {

    private final Greeter greeter;
    private final ObjectProvider<FestivalBanner> banner;

    // ObjectProvider: "a FestivalBanner if there is one". The banner bean may not exist at all.
    public GreetingController(Greeter greeter, ObjectProvider<FestivalBanner> banner) {
        this.greeter = greeter;
        this.banner = banner;
    }

    @GetMapping("/greeting")
    public String greeting() {
        return greeter.greet();
    }

    @GetMapping("/banner")
    public String banner() {
        FestivalBanner b = banner.getIfAvailable();
        return b == null ? "No festival today" : b.text();
    }
}
