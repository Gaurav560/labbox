package com.shop.check;

import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;

@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext
class Ch15Check {
    @Autowired
    MockMvc mvc;
    final ObjectMapper json = new ObjectMapper();

    Map<?, ?> product(long id) throws Exception {
        return json.readValue(mvc.perform(get("/products/" + id)).andReturn().getResponse().getContentAsString(), Map.class);
    }

    @Test
    void putProduct() {
        R.task("put_product", () -> {
            MvcResult r = mvc.perform(put("/products/2").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Filter coffee (large)\", \"pricePaise\": 3500, \"stock\": 20}")).andReturn();
            int code = r.getResponse().getStatus();
            int missing = mvc.perform(put("/products/99").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Ghost\", \"pricePaise\": 1, \"stock\": 1}")).andReturn().getResponse().getStatus();
            if (code == 405) {
                R.fail("put_product", "PUT /products/2 answers 405: there is no PUT method for that path yet.", "200", "405");
                return;
            }
            Map<?, ?> p = product(2);
            if (code != 200 || !"Filter coffee (large)".equals(p.get("name")) || !Integer.valueOf(3500).equals(p.get("pricePaise")) || !Integer.valueOf(20).equals(p.get("stock"))) {
                R.fail("put_product", "PUT /products/2 should replace the product with the body, and GET /products/2 should then show it.", "200, then {name: Filter coffee (large), pricePaise: 3500, stock: 20}", code + ", then " + p);
            } else if (!Integer.valueOf(2).equals(p.get("id"))) {
                R.fail("put_product", "The id must stay the one from the path.", "id 2", "id " + p.get("id"));
            } else if (missing != 404) {
                R.fail("put_product", "PUT on a product that does not exist should answer 404 (and not create it).", "404", String.valueOf(missing));
            } else {
                R.pass("put_product", "PUT replaced the whole product, kept the id from the path, and refused an unknown id with 404.");
            }
        });
    }

    @Test
    void patchPrice() {
        R.task("patch_price", () -> {
            MvcResult r = mvc.perform(patch("/products/1").contentType(MediaType.APPLICATION_JSON).content("{\"pricePaise\": 2200}")).andReturn();
            int code = r.getResponse().getStatus();
            int missing = mvc.perform(patch("/products/99").contentType(MediaType.APPLICATION_JSON).content("{\"stock\": 5}")).andReturn().getResponse().getStatus();
            if (code == 405) {
                R.fail("patch_price", "PATCH /products/1 answers 405: there is no PATCH method for that path yet.", "200", "405");
                return;
            }
            Map<?, ?> p = product(1);
            if (code != 200 || !Integer.valueOf(2200).equals(p.get("pricePaise"))) {
                R.fail("patch_price", "PATCH /products/1 with only a price should change the price.", "pricePaise 2200", code + ", " + p);
            } else if (!"Mango lassi".equals(p.get("name")) || !Integer.valueOf(40).equals(p.get("stock"))) {
                R.fail("patch_price", "The fields that were not sent must keep their old values: a null in the ProductPatch means keep it.", "{name: Mango lassi, pricePaise: 2200, stock: 40}", String.valueOf(p));
            } else if (missing != 404) {
                R.fail("patch_price", "PATCH on a product that does not exist should answer 404.", "404", String.valueOf(missing));
            } else {
                R.pass("patch_price", "PATCH changed only what was sent: the price moved, the name and the stock stayed.");
            }
        });
    }
}
