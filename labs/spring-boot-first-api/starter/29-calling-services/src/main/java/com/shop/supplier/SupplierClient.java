package com.shop.supplier;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Asks the supplier how many of an item it has, at GET {supplier.base-url}/stock/{sku}. */
@Component
public class SupplierClient {

    /** The supplier's answer: {"sku": "KUL-1", "available": 120}. */
    public record SupplierStock(String sku, int available) {
    }

    private final RestClient http;

    public SupplierClient(RestClient.Builder builder, @Value("${supplier.base-url}") String baseUrl) {
        // TODO (task handle_supplier_errors): give the client a read timeout of 1 second (a
        // SimpleClientHttpRequestFactory with setReadTimeout), so a slow supplier cannot hang the shop.
        this.http = builder.baseUrl(baseUrl).build();
    }

    /** How many the supplier has. A 404 from the supplier means it does not stock the item: 0. */
    public int available(String sku) {
        // TODO (task fetch_stock): GET /stock/{sku}, read the JSON into SupplierStock, return available.
        // TODO (task handle_supplier_errors): when the supplier answers 404, return 0.
        return -1;
    }
}
