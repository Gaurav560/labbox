package com.shop.check;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch05Check {
    @Autowired
    MockMvc mvc;
    final ObjectMapper json = new ObjectMapper();

    private List<String> names(String url) throws Exception {
        MvcResult r = mvc.perform(get(url)).andReturn();
        if (r.getResponse().getStatus() != 200) {
            return null;
        }
        List<Map<String, Object>> list = json.readValue(r.getResponse().getContentAsString(), new TypeReference<>() {});
        return list.stream().map(m -> String.valueOf(m.get("name"))).toList();
    }

    @Test
    void productById() {
        R.task("product_by_id", () -> {
            MvcResult one = mvc.perform(get("/products/3")).andReturn();
            int missing = mvc.perform(get("/products/99")).andReturn().getResponse().getStatus();
            String b = one.getResponse().getContentAsString();
            Object name = one.getResponse().getStatus() == 200 ? json.readValue(b, Map.class).get("name") : null;
            if (!"Samosa".equals(name)) {
                R.fail("product_by_id", "GET /products/3 should return the Samosa as JSON.", "200 {\"id\":3,\"name\":\"Samosa\",...}", one.getResponse().getStatus() + " " + b);
            } else if (missing != 404) {
                R.fail("product_by_id", "An unknown id should answer 404, not " + missing + ". Throw a ResponseStatusException with HttpStatus.NOT_FOUND.", "404", String.valueOf(missing));
            } else {
                R.pass("product_by_id", "{id} in the path became a long parameter, and a missing product is an honest 404.");
            }
        });
    }

    @Test
    void searchProducts() {
        R.task("search_products", () -> {
            List<String> all = names("/products/search");
            if (all == null) {
                R.fail("search_products", "GET /products/search is not mapped yet.");
                return;
            }
            List<String> cheap = names("/products/search?maxPrice=2000");
            List<String> byPrice = names("/products/search?sort=price");
            List<String> wantAll = List.of("Filter coffee", "Mango lassi", "Paneer roll", "Samosa");
            if (!all.equals(wantAll)) {
                R.fail("search_products", "Without parameters, the search should return every product sorted by name.", wantAll.toString(), all.toString());
            } else if (!List.of("Mango lassi", "Samosa").equals(cheap)) {
                R.fail("search_products", "maxPrice=2000 should keep only products costing 2000 paise or less, sorted by name.", "[Mango lassi, Samosa]", String.valueOf(cheap));
            } else if (!List.of("Samosa", "Mango lassi", "Filter coffee", "Paneer roll").equals(byPrice)) {
                R.fail("search_products", "sort=price should list the cheapest first.", "[Samosa, Mango lassi, Filter coffee, Paneer roll]", String.valueOf(byPrice));
            } else {
                R.pass("search_products", "Optional query parameters with sensible defaults: one endpoint answers many questions.");
            }
        });
    }
}
