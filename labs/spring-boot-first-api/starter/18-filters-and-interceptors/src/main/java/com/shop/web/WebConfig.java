package com.shop.web;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/** Spring MVC settings for the shop. */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final HandledByInterceptor handledBy;

    public WebConfig(HandledByInterceptor handledBy) {
        this.handledBy = handledBy;
    }

    // TODO (task handled_by_interceptor): register handledBy (override addInterceptors), for the API's paths
    // only: /api/** (not /ping).
}
