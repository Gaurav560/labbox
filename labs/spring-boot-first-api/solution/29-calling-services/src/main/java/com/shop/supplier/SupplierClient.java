package com.shop.supplier;

import java.time.Duration;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

/** Asks the supplier how many of an item it has, at GET {supplier.base-url}/stock/{sku}. */
@Component
public class SupplierClient {

    /** The supplier's answer: {"sku": "KUL-1", "available": 120}. */
    public record SupplierStock(String sku, int available) {
    }

    private final RestClient http;

    public SupplierClient(RestClient.Builder builder, @Value("${supplier.base-url}") String baseUrl) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(1));
        factory.setReadTimeout(Duration.ofSeconds(1));
        this.http = builder.baseUrl(baseUrl).requestFactory(factory).build();
    }

    /** How many the supplier has. A 404 from the supplier means it does not stock the item: 0. */
    public int available(String sku) {
        try {
            SupplierStock s = http.get().uri("/stock/{sku}", sku).retrieve().body(SupplierStock.class);
            return s == null ? 0 : s.available();
        } catch (HttpClientErrorException e) {
            if (e.getStatusCode().value() == 404) {
                return 0;
            }
            throw e;
        }
    }
}
