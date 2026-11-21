package com.shop.check;

import java.io.FileReader;
import java.util.Map;
import java.util.Properties;

import org.junit.jupiter.api.Test;

/** Chapter 1: the learner's answers.properties holds what the menu API really answered. */
class Ch01Check {

    static Properties answers() throws Exception {
        Properties p = new Properties();
        try (FileReader r = new FileReader("answers.properties")) {
            p.load(r);
        }
        return p;
    }

    static void check(String task, Map<String, String> expected, Map<String, String> advice, String passMessage) {
        R.task(task, () -> {
            Properties p = answers();
            for (var e : expected.entrySet()) {
                String got = p.getProperty(e.getKey(), "").trim();
                if (got.isEmpty()) {
                    R.fail(task, e.getKey() + " is still empty. " + advice.get(e.getKey()));
                    return;
                }
                if (!got.equalsIgnoreCase(e.getValue())) {
                    R.fail(task, e.getKey() + " is not what the server answered. " + advice.get(e.getKey()), e.getValue(), got);
                    return;
                }
            }
            R.pass(task, passMessage);
        });
    }

    @Test
    void httpStatus() {
        check("http_status",
                Map.of("status_for_menu", "200", "status_for_missing_item", "404", "content_type_for_menu", "application/json"),
                Map.of("status_for_menu", "Run curl -i localhost:8080/menu and read the number on the first line.",
                        "status_for_missing_item", "Run curl -i localhost:8080/menu/42: the first line has the status.",
                        "content_type_for_menu", "Look for the Content-Type line in the headers of curl -i localhost:8080/menu."),
                "200 for found, 404 for not found, and JSON announced in Content-Type: you read a real HTTP response.");
    }

    @Test
    void httpMethods() {
        check("http_methods",
                Map.of("status_after_post", "201", "location_after_post", "/menu/4", "status_after_delete", "204"),
                Map.of("status_after_post", "Send the POST from the lesson with curl -i and read the first line of the answer.",
                        "location_after_post", "The Location header is in the headers of that same POST answer.",
                        "status_after_delete", "Run curl -i -X DELETE localhost:8080/menu/2 and read the first line."),
                "201 Created with a Location, then 204 No Content: you created and removed data with the right methods.");
    }
}
