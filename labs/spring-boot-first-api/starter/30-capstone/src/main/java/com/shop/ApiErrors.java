package com.shop;

import org.springframework.web.bind.annotation.RestControllerAdvice;

// TODO (task checkout_errors): answer errors as ProblemDetail:
//   OutOfStockException -> 409, title "Out of stock", the exception's message as detail, and a
//   property "sku";
//   MethodArgumentNotValidException -> 400, title "Invalid request", and an "errors" map of field to message.
@RestControllerAdvice
public class ApiErrors {
}
