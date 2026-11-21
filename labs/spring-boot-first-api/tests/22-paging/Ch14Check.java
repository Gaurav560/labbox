package com.shop.check;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.Arrays;

import com.shop.product.ProductRepository;
import org.springframework.data.jpa.repository.Query;

@SpringBootTest
@AutoConfigureMockMvc
class Ch14Check {
    @Autowired
    MockMvc mvc;
    final ObjectMapper json = new ObjectMapper();

    @Test
    void pagedProducts() {
        R.task("paged_products", () -> {
            String body = mvc.perform(get("/products?page=1&size=2&sort=name")).andReturn().getResponse().getContentAsString();
            Map<?, ?> page = body.startsWith("{") ? json.readValue(body, Map.class) : Map.of();
            Object content = page.get("content");
            Map<?, ?> meta = page.get("page") instanceof Map<?, ?> m ? m : Map.of();
            List<?> names = content instanceof List<?> l ? l.stream().map(x -> ((Map<?, ?>) x).get("name")).toList() : List.of();
            if (!(content instanceof List)) {
                R.fail("paged_products", "GET /products should return a page (with content and page fields), not a plain list.", "{\"content\": [...], \"page\": {...}}", body.length() > 120 ? body.substring(0, 120) + "..." : body);
            } else if (!Integer.valueOf(6).equals(meta.get("totalElements")) || !names.equals(List.of("Kachori", "Masala tea"))) {
                R.fail("paged_products", "Page 1 (the second page) of 2, sorted by name, should hold Kachori and Masala tea, out of 6 products.", "[Kachori, Masala tea], totalElements 6", names + ", totalElements " + meta.get("totalElements"));
            } else {
                R.pass("paged_products", "Pageable turned ?page=1&size=2&sort=name into LIMIT, OFFSET and ORDER BY, and the page reports the total for the client.");
            }
        });
    }

    @Test
    void priceRange() {
        R.task("price_range", () -> {
            boolean annotated = Arrays.stream(ProductRepository.class.getDeclaredMethods())
                    .anyMatch(m -> m.getName().equals("inPriceRange") && m.isAnnotationPresent(Query.class));
            String body = mvc.perform(get("/products/price-range?min=2000&max=3000")).andReturn().getResponse().getContentAsString();
            List<Map<String, Object>> list = json.readValue(body, new TypeReference<>() {});
            List<Object> names = list.stream().map(m -> m.get("name")).toList();
            if (!annotated) {
                R.fail("price_range", "ProductRepository needs a method inPriceRange marked with @Query.");
            } else if (!names.equals(List.of("Masala tea", "Kachori", "Vada pav", "Filter coffee"))) {
                R.fail("price_range", "min=2000&max=3000 should list the products from 2000 to 3000 paise, both included, cheapest first.", "[Masala tea, Kachori, Vada pav, Filter coffee]", names.toString());
            } else {
                R.pass("price_range", "A JPQL query with named parameters: BETWEEN includes both ends, and ORDER BY ran in the database.");
            }
        });
    }
}
