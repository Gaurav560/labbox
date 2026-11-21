package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@SpringBootTest
@AutoConfigureMockMvc
class Ch07Check {
    @Autowired
    MockMvc mvc;

    @Test
    void created201() {
        R.task("created_201", () -> {
            MvcResult r = mvc.perform(post("/products").contentType(MediaType.APPLICATION_JSON)
                    .content("{\"name\": \"Poha\", \"pricePaise\": 2200}")).andReturn();
            int code = r.getResponse().getStatus();
            String location = r.getResponse().getHeader("Location");
            String body = r.getResponse().getContentAsString();
            if (code != 201) {
                R.fail("created_201", "Creating a product should answer 201 Created, not " + code + ".", "201", String.valueOf(code));
            } else if (location == null || !location.matches(".*/products/[0-9]+$")) {
                R.fail("created_201", "A 201 needs a Location header with the new product's URL, like /products/4.", "/products/4", String.valueOf(location));
            } else if (!body.contains("Poha")) {
                R.fail("created_201", "Send the created product in the body too.");
            } else {
                R.pass("created_201", "201 Created plus a Location header: the client knows it worked and where the new product lives.");
            }
        });
    }

    @Test
    void delete204() {
        R.task("delete_204", () -> {
            int first = mvc.perform(delete("/products/3")).andReturn().getResponse().getStatus();
            int again = mvc.perform(delete("/products/3")).andReturn().getResponse().getStatus();
            if (first != 204) {
                R.fail("delete_204", "Deleting an existing product should answer 204 No Content, not " + first + ".", "204", String.valueOf(first));
            } else if (again != 404) {
                R.fail("delete_204", "Deleting it a second time should answer 404: there is nothing to delete.", "404", String.valueOf(again));
            } else {
                R.pass("delete_204", "204 when it worked, 404 when there was nothing there: the status code alone tells the client what happened.");
            }
        });
    }
}
