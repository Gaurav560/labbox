package com.shop.product;

import java.util.List;

import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<Product> all() {
        return repository.findAll();
    }

    public Product get(long id) {
        return repository.findById(id).orElseThrow(() -> new ProductNotFoundException(id));
    }

    public Product create(NewProduct p) {
        return repository.add(p.name(), p.pricePaise(), 0);
    }
}
