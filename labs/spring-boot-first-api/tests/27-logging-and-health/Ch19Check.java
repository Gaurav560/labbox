package com.shop.check;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;
import org.springframework.test.web.servlet.MockMvc;

import com.shop.stock.StockService;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
@ExtendWith(OutputCaptureExtension.class)
class Ch19Check {
    @Autowired
    MockMvc mvc;
    @Autowired
    StockService stock;

    @Test
    void healthInfo() {
        R.task("health_info", () -> {
            var health = mvc.perform(get("/actuator/health")).andReturn().getResponse();
            var info = mvc.perform(get("/actuator/info")).andReturn().getResponse();
            if (health.getStatus() != 200 || !health.getContentAsString().contains("UP")) {
                R.fail("health_info", "GET /actuator/health should answer 200 with status UP.", "200 {\"status\":\"UP\"}", health.getStatus() + " " + health.getContentAsString());
            } else if (info.getStatus() != 200) {
                R.fail("health_info", "GET /actuator/info answers " + info.getStatus() + ": expose info as well as health over HTTP.", "200", String.valueOf(info.getStatus()));
            } else if (!info.getContentAsString().contains("Shop API")) {
                R.fail("health_info", "The info endpoint does not show the app name yet: set info.app.name and turn on management.info.env.enabled.", "{\"app\":{\"name\":\"Shop API\"}}", info.getContentAsString());
            } else {
                R.pass("health_info", "Health for the load balancer and info for people: Actuator answers both, configured with properties only.");
            }
        });
    }

    @Test
    void logWarning(CapturedOutput output) {
        R.task("log_warning", () -> {
            stock.take("SAM-1");
            String out = output.getAll();
            boolean line = out.lines().anyMatch(l -> l.contains("WARN") && l.contains("Out of stock: SAM-1") && l.contains("StockService"));
            if (out.contains("out of stock SAM-1")) {
                R.fail("log_warning", "The message is still printed with System.out.println. Log it with an SLF4J Logger instead.");
            } else if (!line) {
                R.fail("log_warning", "No WARN log line with Out of stock: SAM-1 from StockService was found.", "... WARN ... StockService : Out of stock: SAM-1", "(no such line)");
            } else {
                R.pass("log_warning", "A WARN line with a timestamp, the thread and the class: something a log search or an alert can find.");
            }
        });
    }
}
