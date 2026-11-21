package com.shop;

import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Turns exceptions from any controller into one consistent error format (RFC 9457, ProblemDetail). */
@RestControllerAdvice
public class ApiErrors {

    // TODO (task not_found_problem): handle ProductNotFoundException: answer 404 with a ProblemDetail whose
    // title is "Product not found" and whose detail is the exception's message.

    // TODO (task validation_problem): handle MethodArgumentNotValidException: answer 400 with a ProblemDetail
    // titled "Invalid request" and a property "errors": a map from each field name to its message.
}
