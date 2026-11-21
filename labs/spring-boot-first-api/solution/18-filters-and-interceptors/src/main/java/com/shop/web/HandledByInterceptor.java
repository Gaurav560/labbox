package com.shop.web;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

/** Before a controller method runs, adds a header naming it: X-Handled-By: ProductController#all. */
@Component
public class HandledByInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if (handler instanceof HandlerMethod method) {
            response.setHeader("X-Handled-By", method.getBeanType().getSimpleName() + "#" + method.getMethod().getName());
        }
        return true;   // true: carry on to the controller. false would stop the request here.
    }
}
