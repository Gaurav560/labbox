package com.shop.web;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/** Spring MVC settings for the shop. */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final HandledByInterceptor handledBy;

    public WebConfig(HandledByInterceptor handledBy) {
        this.handledBy = handledBy;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(handledBy).addPathPatterns("/api/**");
    }
}
