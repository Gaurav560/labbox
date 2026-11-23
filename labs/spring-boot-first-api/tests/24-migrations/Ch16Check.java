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

import org.springframework.jdbc.core.JdbcTemplate;

@SpringBootTest
@AutoConfigureMockMvc
class Ch16Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    JdbcTemplate jdbc;

    List<String> versions() {
        return jdbc.queryForList("SELECT \"version\" FROM \"flyway_schema_history\" WHERE \"success\" = TRUE AND \"version\" IS NOT NULL ORDER BY \"installed_rank\"", String.class);
    }

    @Test
    void addCategoryColumn() {
        R.task("add_category_column", () -> {
            List<String> v = versions();
            String body = mvc.perform(get("/products")).andReturn().getResponse().getContentAsString();
            if (!v.contains("2")) {
                R.fail("add_category_column", "There is no version 2 migration yet. Add V2__add_category.sql next to V1.", "versions [1, 2]", v.toString());
            } else if (!body.contains("\"category\"")) {
                R.fail("add_category_column", "The products have no category in the response yet.");
            } else {
                R.pass("add_category_column", "Flyway ran V2 once and recorded it; Hibernate validated that the table now matches the entity.");
            }
        });
    }

    @Test
    void setCategories() {
        R.task("set_categories", () -> {
            List<String> v = versions();
            Map<String, Object> cats = new java.util.HashMap<>();
            jdbc.queryForList("SELECT sku, category FROM product").forEach(r -> cats.put(String.valueOf(r.get("SKU")), r.get("CATEGORY")));
            boolean right = "sweets".equals(cats.get("KUL-1")) && "sweets".equals(cats.get("CUS-1")) && "snacks".equals(cats.get("SAM-1"));
            if (!v.equals(List.of("1", "2", "3"))) {
                R.fail("set_categories", "Flyway should have applied versions 1, 2 and 3, in order.", "[1, 2, 3]", v.toString());
            } else if (!right) {
                R.fail("set_categories", "After V3, KUL-1 and CUS-1 should be sweets and SAM-1 snacks.", "{KUL-1=sweets, CUS-1=sweets, SAM-1=snacks}", cats.toString());
            } else {
                R.pass("set_categories", "Three versioned migrations, applied in order on every new database: the schema has a history, like your code.");
            }
        });
    }
}
