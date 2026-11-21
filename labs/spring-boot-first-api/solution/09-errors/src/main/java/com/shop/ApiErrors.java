package com.shop;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.shop.product.ProductNotFoundException;

/** Turns exceptions from any controller into one consistent error format (RFC 9457, ProblemDetail). */
@RestControllerAdvice
public class ApiErrors {

    @ExceptionHandler(ProductNotFoundException.class)
    public ProblemDetail notFound(ProductNotFoundException e) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
        p.setTitle("Product not found");
        return p;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail invalid(MethodArgumentNotValidException e) {
        Map<String, String> errors = new LinkedHashMap<>();
        e.getBindingResult().getFieldErrors().forEach(f -> errors.put(f.getField(), f.getDefaultMessage()));
        ProblemDetail p = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        p.setTitle("Invalid request");
        p.setProperty("errors", errors);
        return p;
    }
}
