package com.shop.product;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    ProductRepository repository;

    @Test
    void findsOneCategorySortedByName() {
        repository.save(new Product("Samosa", "snacks"));
        repository.save(new Product("Mango lassi", "drinks"));
        repository.save(new Product("Bhel puri", "snacks"));
        repository.save(new Product("Kachori", "snacks"));

        List<String> names = repository.findByCategoryOrderByNameAsc("snacks").stream().map(Product::getName).toList();

        assertThat(names).containsExactly("Bhel puri", "Kachori", "Samosa");
    }
}
