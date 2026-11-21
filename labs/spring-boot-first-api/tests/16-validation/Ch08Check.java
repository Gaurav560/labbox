package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@SpringBootTest
@AutoConfigureMockMvc
class Ch08Check {
    @Autowired
    MockMvc mvc;

    int send(String url, String json) throws Exception {
        return mvc.perform(post(url).contentType(MediaType.APPLICATION_JSON).content(json)).andReturn().getResponse().getStatus();
    }

    @Test
    void validateProduct() {
        R.task("validate_product", () -> {
            String[][] bad = {{"{\"name\": \"\", \"pricePaise\": 2000}", "an empty name"},
                    {"{\"name\": \"Tea\", \"pricePaise\": 0}", "a price of 0"},
                    {"{\"name\": \"Tea\", \"pricePaise\": -5}", "a negative price"},
                    {"{\"name\": \"" + "x".repeat(41) + "\", \"pricePaise\": 2000}", "a 41-character name"}};
            for (String[] b : bad) {
                int code = send("/products", b[0]);
                if (code != 400) {
                    R.fail("validate_product", "A product with " + b[1] + " was accepted (" + code + "). Add the constraints to NewProduct and @Valid before @RequestBody.", "400", String.valueOf(code));
                    return;
                }
            }
            int ok = send("/products", "{\"name\": \"Tea\", \"pricePaise\": 2000}");
            if (ok != 201) {
                R.fail("validate_product", "A valid product should still be created.", "201", String.valueOf(ok));
            } else {
                R.pass("validate_product", "Bean Validation checked the body before your method ran: bad data gets a 400 and never reaches the shop.");
            }
        });
    }

    @Test
    void validateCustomer() {
        R.task("validate_customer", () -> {
            String[][] bad = {{"{\"name\": \"\", \"email\": \"asha@shop.in\", \"phone\": \"9876543210\"}", "an empty name"},
                    {"{\"name\": \"Asha\", \"email\": \"not-an-email\", \"phone\": \"9876543210\"}", "an invalid email"},
                    {"{\"name\": \"Asha\", \"email\": \"asha@shop.in\", \"phone\": \"98765\"}", "a 5-digit phone"},
                    {"{\"name\": \"Asha\", \"email\": \"asha@shop.in\", \"phone\": \"98765abcde\"}", "letters in the phone"}};
            for (String[] b : bad) {
                int code = send("/customers", b[0]);
                if (code != 400) {
                    R.fail("validate_customer", "A customer with " + b[1] + " was accepted (" + code + ").", "400", String.valueOf(code));
                    return;
                }
            }
            int ok = send("/customers", "{\"name\": \"Asha\", \"email\": \"asha@shop.in\", \"phone\": \"9876543210\"}");
            if (ok != 201) {
                R.fail("validate_customer", "A valid customer should still be created.", "201", String.valueOf(ok));
            } else {
                R.pass("validate_customer", "@NotBlank, @Email and @Pattern: the rules live on the record, next to the data they protect.");
            }
        });
    }
}
