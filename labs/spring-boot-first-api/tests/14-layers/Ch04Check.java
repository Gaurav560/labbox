package com.shop.check;

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.SpyBean;
import org.springframework.test.web.servlet.MockMvc;

import com.shop.product.ProductRepository;
import com.shop.product.ProductService;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch04Check {
    @Autowired
    MockMvc mvc;
    @SpyBean
    ProductService service;
    @SpyBean
    ProductRepository repository;

    @Test
    void thinController() {
        R.task("thin_controller", () -> {
            Mockito.clearInvocations(service);
            String got = mvc.perform(get("/products/average-price")).andReturn().getResponse().getContentAsString();
            int direct = service.averagePrice();
            boolean delegated = Mockito.mockingDetails(service).getInvocations().stream()
                    .filter(i -> i.getMethod().getName().equals("averagePrice")).count() >= 2;
            if (direct != 3950) {
                R.fail("thin_controller", "ProductService.averagePrice() should work out the average of the four prices.", "3950", String.valueOf(direct));
            } else if (!delegated) {
                R.fail("thin_controller", "ProductService.averagePrice() is right, but GET /products/average-price does not call it: the controller still does the work itself.");
            } else if (!got.equals("3950")) {
                R.fail("thin_controller", "GET /products/average-price should answer the service's result.", "3950", got);
            } else {
                R.pass("thin_controller", "The controller only translates HTTP; the rule lives in the service, where any other caller can reuse it and a test can check it.");
            }
        });
    }

    @Test
    void budgetProducts() {
        R.task("budget_products", () -> {
            Mockito.clearInvocations(repository);
            String got = mvc.perform(get("/products/budget")).andReturn().getResponse().getContentAsString();
            boolean viaRepo = Mockito.mockingDetails(repository).getInvocations().stream()
                    .anyMatch(i -> i.getMethod().getName().equals("findCheaperThan"));
            boolean right = got.contains("Mango kulfi") && got.contains("Fruit custard") && got.contains("Samosa") && !got.contains("Paneer roll");
            if (!right) {
                R.fail("budget_products", "GET /products/budget should list the three products under Rs 50 (5000 paise).", "Mango kulfi, Fruit custard, Samosa", got);
            } else if (!viaRepo) {
                R.fail("budget_products", "The list is right, but the service does not ask the repository's findCheaperThan for it.");
            } else {
                R.pass("budget_products", "Each layer does one job: the controller asks the service, the service applies the Rs 50 rule, and the repository fetches the data.");
            }
        });
    }
}
