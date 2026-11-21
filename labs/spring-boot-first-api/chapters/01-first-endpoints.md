:::step{type=story title="Why this chapter"}
An API is a set of URLs that a program answers. This chapter adds the Shop API's first two endpoints:
one that returns text and one that returns JSON, the format almost every web and mobile app uses.

:::mission
Add `GET /hello` and `GET /merchants` to the Shop API, and see both answer in the Preview tab.
:::
:::

:::step{type=concept title="A controller answers URLs"}
A class marked `@RestController` answers HTTP requests. Each method with a mapping annotation handles
one HTTP method and path:

```java
@RestController
public class StatusController {

    @GetMapping("/status")
    public String status() {
        return "all good";
    }
}
```

- `@RestController` tells Spring to create this class at start-up and to send method results back as the response body.
- `@GetMapping("/status")` maps `GET /status` to `status()`.
- The return value becomes the response.

At start-up, Spring scans the application's package, finds the class and registers the mapping.
:::

:::step{type=predict title="Guess first"}
:::question
`status()` returns a `String`. What does the client receive for `GET /status`?
:::
- [x] The plain text `all good`
- [ ] A JSON object `{"status": "all good"}`
- [ ] A Java object it has to deserialize
:::explain
A `String` is written as plain text. Objects and lists are converted to JSON instead, as the next
example shows.
:::
:::

:::step{type=try title="Build and run"}
Build the app and start it:

```bash run
mvn -q -o package -DskipTests && java -jar target/shop-api.jar
```

When you see `Started ShopApiApplication`, open the **Preview** tab. It shows a 404 page for now:
nothing is mapped to `/hello` yet. Stop the app with Ctrl+C before you build again.
:::

:::step{type=task task=hello title="Warm-up: say hello"}
In `MerchantController`, add `GET /hello` returning the text `Hello from the Shop API!`.
Build, start, and reload the Preview.
:::

:::step{type=example title="Worked example: lists become JSON"}
Return a `List` and Spring converts it to a JSON array, using the Jackson library from the web starter:

```java
@GetMapping("/cities")
public List<String> cities() {
    return List.of("Pune", "Indore", "Kochi");
}
```

`GET /cities` answers:

```json
["Pune","Indore","Kochi"]
```

The same happens for objects: their fields become JSON properties, as you will see in chapter 6.

:::mistake
`List.of(...)` creates an unmodifiable list: calling `sort()` on it throws an exception. Sort a copy,
for example with `stream().sorted().toList()`.
:::
:::

:::step{type=task task=merchants title="List the merchants"}
Add `GET /merchants` returning the names in `MERCHANTS`, sorted A to Z, as JSON:
`["Annapurna Mess","Brew Point","Kirana King"]`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A method mapped with `@GetMapping("/items")` returns `List.of(3, 1, 2)`. What does `GET /items` answer?
:::
- [ ] `3 1 2` as text
- [x] The JSON array `[3,1,2]`
- [ ] `[1,2,3]`, sorted
:::explain
Lists become JSON arrays, in their own order. Spring does not sort anything for you.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You added a new method but `GET /hello` still answers 404. What is the most likely reason?
:::
- [ ] Spring needs a restart of the computer
- [x] The app is still running the old build: stop it, build again and start it
- [ ] `@GetMapping` only works for JSON
:::explain
The running `jar` contains the code from the last build. Stop it, rebuild, and start it again.
:::
:::

:::step{type=deep-dive title="What happens on a request"}
When `GET /hello` arrives, the embedded **Tomcat** server reads it and passes it to Spring's
**DispatcherServlet**, the single entry point for every request. The DispatcherServlet looks up which
method is mapped to `GET /hello` (it built that table at start-up), calls it, and passes the return value
to a **message converter**: a `String` goes out as `text/plain`, a `List` or object goes through Jackson
as `application/json`. All of this is configured automatically by the web starter.
:::

:::step{type=recap title="Chapter done"}
- `@RestController` classes answer HTTP requests; `@GetMapping("/path")` maps one URL to one method.
- A `String` is sent as plain text; a `List` or an object becomes JSON.
- Build with `mvn package`, run the `jar`, and check it in the Preview.
:::
