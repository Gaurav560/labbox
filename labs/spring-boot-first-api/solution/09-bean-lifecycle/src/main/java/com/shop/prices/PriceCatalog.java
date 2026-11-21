package com.shop.prices;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

/** Every product's price, read once from prices.csv so each request does not read the file again. */
@Component
public class PriceCatalog {

    private static final Logger log = LoggerFactory.getLogger(PriceCatalog.class);

    private final Map<String, Integer> prices = new HashMap<>();

    @PostConstruct
    public void load() throws IOException {
        var file = new ClassPathResource("prices.csv").getInputStream();
        try (var lines = new BufferedReader(new InputStreamReader(file, StandardCharsets.UTF_8))) {
            lines.lines().skip(1).forEach(line -> {
                String[] parts = line.split(",");
                prices.put(parts[0], Integer.parseInt(parts[1]));
            });
        }
        log.info("Loaded {} prices", prices.size());
    }

    public Optional<Integer> price(String sku) {
        return Optional.ofNullable(prices.get(sku));
    }

    public int count() {
        return prices.size();
    }
}
