package com.shop.web;

import java.io.IOException;
import java.util.UUID;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/** Gives every request an id, so one request can be followed through the logs of every service. */
@Component
public class RequestIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String id = request.getHeader("X-Request-Id");
        if (id == null || id.isBlank()) {
            id = UUID.randomUUID().toString();
        }
        response.setHeader("X-Request-Id", id);
        chain.doFilter(request, response);
    }
}
