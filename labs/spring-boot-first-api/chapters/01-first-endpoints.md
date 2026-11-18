:::step{type=story title="The dashboard needs a backend"}
:::character{name="Kabir" role="Lead engineer, PaySetu"}
Our merchant dashboard still reads from a spreadsheet. Today we start the real
backend in Spring Boot, the same stack most Indian fintechs run on. Two endpoints
to begin with, and I want to see them answer in a browser.
:::

:::mission
Add `GET /hello` and `GET /merchants` to the merchant API, and see both live.
:::
:::

:::step{type=concept title="A controller answers URLs"}
In Spring Boot, a class marked `@RestController` answers web requests. Each method
with a mapping annotation handles one URL:

```java
@RestController
public class StatusController {
    @GetMapping("/status")
    public String status() {
        return "all good";
    }
}
```

Spring scans your package at start-up, finds the controller, and wires the URL
to the method. No configuration file needed.
:::

:::step{type=predict title="Guess first"}
:::question
`status()` returns a `String`. What does the browser receive for `GET /status`?
:::
- [x] The plain text `all good`
- [ ] A JSON object `{"status": "all good"}`
- [ ] A Java object it has to deserialize
:::explain
A `String` from a `@RestController` method is sent as plain text. Lists and objects
are turned into JSON instead, which you will see in the next task.
:::
:::

:::step{type=try title="Build and run"}
Build the app and start it. The first build takes a few seconds:

```bash run
mvn -q package -DskipTests && java -jar target/merchant-api.jar
```

When you see `Started MerchantApiApplication`, open the **Preview** tab. It shows a
404 page for now: there is no `/hello` yet. Stop the app with Ctrl+C before rebuilding.
:::

:::step{type=task task=hello title="Say hello"}
In `MerchantController`, add `GET /hello` returning the text `Hello from PaySetu!`.
Rebuild, restart, and reload the Preview.
:::

:::step{type=example title="Lists become JSON"}
Return a list and Spring (with the Jackson library) writes a JSON array:

```java
@GetMapping("/cities")
public List<String> cities() {
    return List.of("Pune", "Indore", "Kochi");
}
```

`GET /cities` answers `["Pune","Indore","Kochi"]`.

:::mistake
`List.of(...)` gives an unmodifiable list: calling `sort()` on it throws an exception.
Sort a copy instead.
:::
:::

:::step{type=task task=merchants title="List the merchants"}
Add `GET /merchants` returning the names in `MERCHANTS`, sorted A to Z, as JSON:
`["Annapurna Mess","Chai Point","Kirana King"]`.
:::

:::step{type=recap}
- `@RestController` classes answer web requests; `@GetMapping("/path")` maps one URL.
- A `String` is sent as plain text, a `List` becomes a JSON array.
- Build with `mvn package`, run the jar, and check it live in the Preview.
:::
