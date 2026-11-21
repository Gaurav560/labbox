package com.shop.check;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch20Check {
    @Autowired
    MockMvc mvc;

    @Test
    void publicAndProtected() {
        R.task("public_and_protected", () -> {
            int open = mvc.perform(get("/products")).andReturn().getResponse().getStatus();
            int anonymous = mvc.perform(get("/admin/report")).andReturn().getResponse().getStatus();
            int staff = mvc.perform(get("/admin/report").with(httpBasic("staff", "staff123"))).andReturn().getResponse().getStatus();
            int wrong = mvc.perform(get("/admin/report").with(httpBasic("staff", "nope"))).andReturn().getResponse().getStatus();
            if (open != 200) {
                R.fail("public_and_protected", "GET /products should be open to everyone, without a login.", "200", String.valueOf(open));
            } else if (anonymous != 401) {
                R.fail("public_and_protected", "GET /admin/report without a login should answer 401.", "401", String.valueOf(anonymous));
            } else if (staff != 200) {
                R.fail("public_and_protected", "The user staff with password staff123 should be able to read the report.", "200", String.valueOf(staff));
            } else if (wrong != 401) {
                R.fail("public_and_protected", "A wrong password should answer 401.", "401", String.valueOf(wrong));
            } else {
                R.pass("public_and_protected", "One filter chain decides: the product list is public, everything else needs a login.");
            }
        });
    }

    @Test
    void adminOnly() {
        R.task("admin_only", () -> {
            int staff = mvc.perform(delete("/products/1").with(httpBasic("staff", "staff123"))).andReturn().getResponse().getStatus();
            int admin = mvc.perform(delete("/products/1").with(httpBasic("admin", "admin123"))).andReturn().getResponse().getStatus();
            int anonymous = mvc.perform(delete("/products/1")).andReturn().getResponse().getStatus();
            if (anonymous != 401) {
                R.fail("admin_only", "DELETE without a login should answer 401.", "401", String.valueOf(anonymous));
            } else if (staff != 403) {
                R.fail("admin_only", "A logged-in STAFF user deleting a product should get 403 Forbidden.", "403", String.valueOf(staff));
            } else if (admin != 204) {
                R.fail("admin_only", "An ADMIN should be able to delete (204). If you see 403 for admin too, check CSRF is off.", "204", String.valueOf(admin));
            } else {
                R.pass("admin_only", "401 means \"who are you?\", 403 means \"you, but not this\": roles decide what a logged-in user may do.");
            }
        });
    }
}
