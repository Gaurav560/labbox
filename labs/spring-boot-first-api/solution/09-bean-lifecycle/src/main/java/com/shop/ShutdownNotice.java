package com.shop;

import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/** Says goodbye when the app shuts down (Ctrl+C), to show @PreDestroy. */
@Component
public class ShutdownNotice {

    private static final Logger log = LoggerFactory.getLogger(ShutdownNotice.class);

    @PreDestroy
    public void goodbye() {
        log.info("Shop API is shutting down: closing the till for today");
    }
}
