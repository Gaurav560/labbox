:::step{type=story title="The Shop API is not alone"}
A real backend talks to other systems all day: a supplier's API for stock levels, a payment provider to charge
cards, a courier's API for delivery times, an SMS service for order updates. Each of those calls goes over the
network, to a server you do not control. It can be fast, slow, down, or answer something unexpected.

This chapter calls another service with Spring's **`RestClient`**, and, just as important, handles the ways it can
fail. You will run a pretend supplier yourself, in its own terminal, make it misbehave, and watch your API stay calm.
That is a real production skill: most outages in connected systems start with one slow dependency.

:::mission
Read the supplier's stock over HTTP, treat "not stocked" as 0, and answer 503 quickly when the supplier is too slow.
:::
:::

:::step{type=concept title="Your app as a client"}
Since chapter 1, curl has been the client and your app the server. Now your app plays **both** roles in one
request:

```text
curl  ->  Shop API (server)  ->  supplier (server)
          Shop API (client)  <-  supplier's JSON
curl  <-  Shop API's answer
```

A customer asks the Shop API "how many kulfis can the supplier deliver?". The Shop API cannot know; it **asks the
supplier** with its own HTTP request, waits for the answer, and builds its response from it. Everything you know
about HTTP (methods, paths, status codes, JSON) applies, from the other side.

The supplier's API (pretend, but realistic) works like this:

```text
GET /stock/KUL-1     ->  200  {"sku": "KUL-1", "available": 120}
GET /stock/MISSING   ->  404  (the supplier does not stock it)
```
:::

:::step{type=concept title="RestClient"}
**`RestClient`** (Spring Framework 6.1 and later) is Spring's HTTP client. Spring Boot provides a
**`RestClient.Builder`** bean, already set up with the same Jackson JSON handling as your controllers:

```java
RestClient http = builder.baseUrl("https://supplier.example").build();

SupplierStock s = http.get()                       // a GET request...
        .uri("/stock/{sku}", "KUL-1")              // ...to /stock/KUL-1 (the placeholder is filled in, safely encoded)
        .retrieve()                                // send it, and look at the response
        .body(SupplierStock.class);                // read the JSON body into a record
```

Read it as a sentence: get, from this URI, retrieve the response, and give me its body as a `SupplierStock`.
`body(...)` is `@RequestBody` (chapter 12) in reverse: Jackson turns the supplier's JSON into your record, matching
fields by name. Extra fields are ignored.

When the answer is **not** a success, `retrieve()` throws:

- **4xx**: `HttpClientErrorException` (for 404 specifically, `HttpClientErrorException.NotFound`);
- **5xx**: `HttpServerErrorException`;
- **no answer at all** (connection refused, timeout): `ResourceAccessException`.

All three are kinds of **`RestClientException`**, so you can catch them separately or together.
:::

:::step{type=try title="Start the pretend supplier" file="29-calling-services/supplier/FakeSupplier.java"}
The project includes a small **fake supplier**, `supplier/FakeSupplier.java`, on the right. It is a tiny HTTP server
on port **9099**: any sku has 120 available, `MISSING` answers 404, and `SLOW` takes **3 seconds** to answer.

You need three terminals for this chapter (use **+** to open them). In **Terminal 1**, start the supplier (Java can
run a single source file directly):

```bash run
cd 29-calling-services/supplier && java FakeSupplier.java
```

```text
Fake supplier listening on port 9099. Stop it with Ctrl+C.
```

Leave it running. In **Terminal 2**, build and start the Shop API (its `supplier.base-url` setting points to
`http://localhost:9099`):

```bash run
cd 29-calling-services && mvn -q -o package -DskipTests && java -jar target/calling-services.jar
```

In **Terminal 3**, ask the Shop API about kulfi:

```bash run
curl -i localhost:8080/supplier-stock/KUL-1
```

```text
HTTP/1.1 200
{"sku":"KUL-1","available":-1}
```

`-1`: the client code is not written yet, and the supplier's terminal shows nobody called it. (That is our lab
machine's answer. The two keys may come in either order.)
:::

:::step{type=example title="Worked example: a weather client"}
Here is a complete client for a different service, a weather API:

```java
@Component
public class WeatherClient {

    public record Forecast(String city, int celsius) { }

    private final RestClient http;

    public WeatherClient(RestClient.Builder builder, @Value("${weather.base-url}") String baseUrl) {
        this.http = builder.baseUrl(baseUrl).build();
    }

    public int celsius(String city) {
        Forecast f = http.get().uri("/today/{city}", city).retrieve().body(Forecast.class);
        return f.celsius();
    }
}
```

- The client is a **bean**, so controllers and services inject it like anything else.
- The base URL is a **setting** (chapter 7): tests, your laptop and production each point it somewhere else.
- The constructor builds the `RestClient` once; every call reuses it.
:::

:::step{type=task task=fetch_stock title="Your turn: read the supplier's stock"}
In `29-calling-services/src/main/java/com/shop/supplier/SupplierClient.java`, make `available(sku)` call
**`GET /stock/{sku}`** on the supplier, read the JSON into **`SupplierStock`**, and return its **`available`**.

Rebuild and restart the Shop API (Terminal 2), then ask again in Terminal 3:

```bash run
curl localhost:8080/supplier-stock/KUL-1
```

```text
{"available":120,"sku":"KUL-1"}
```

And in Terminal 1, the supplier says `Supplier: someone asked for KUL-1`. Two servers just talked. (Both lines are
what our lab machine showed.) Press **Check**.

Usual slips: `.uri("/stock/" + sku)` built by gluing text (it works for simple skus, but the placeholder form encodes
odd characters safely), forgetting `.retrieve()` before `.body(...)`, or a `SupplierStock` whose field names differ
from the JSON (`stock` instead of `available` leaves the number at 0).
:::

:::step{type=concept title="When the other side says no: 404"}
Now ask about something the supplier does not stock:

```bash run
curl -i localhost:8080/supplier-stock/MISSING
```

The supplier answered 404, so `retrieve()` threw `HttpClientErrorException.NotFound`, nobody caught it, and your
API answered **500**. But for this supplier, 404 is a perfectly normal answer: "we do not stock that". It means
**0 available**, not "the server broke".

This is a decision you make for every call to another service: **what does each of its answers mean for you?**
Here: 200 means "use the number", 404 means "0". You express it with a `try`/`catch` around the call:

```java
try {
    return http.get().uri("/today/{city}", city).retrieve().body(Forecast.class).celsius();
} catch (HttpClientErrorException e) {
    if (e.getStatusCode().value() == 404) {
        return 0;            // unknown city: a normal answer for this API
    }
    throw e;                 // anything else is still an error
}
```
:::

:::step{type=concept title="Timeouts: never wait forever"}
The most dangerous answer is **no answer**. Try the slow item (the supplier waits 3 seconds):

```bash run
curl -i localhost:8080/supplier-stock/SLOW
```

Your request waits the full 3 seconds. Now imagine the supplier is having a bad day and *every* call takes 30
seconds. Each waiting request holds one of Tomcat's worker threads (at most 200 by default, chapter 10). Within a minute, all
200 are waiting on the supplier, and the Shop API stops answering **everyone**, even customers who just want the
product list. One slow dependency has taken your whole app down. This is one of the most common real outages.

The defence is a **timeout**: a limit on how long to wait. After that, give up, and answer quickly:

```java
SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
factory.setConnectTimeout(Duration.ofSeconds(1));   // max time to connect
factory.setReadTimeout(Duration.ofSeconds(1));      // max time to wait for the answer
RestClient http = builder.baseUrl(baseUrl).requestFactory(factory).build();
```

When the time is up, the call throws `ResourceAccessException`. Your API then answers **503 Service Unavailable**,
which means "I am fine, but something I depend on is not, try again later". That is honest, and fast.

:::trace{title="GET /supplier-stock/SLOW, with and without a timeout"}
| time | no timeout | 1 second read timeout |
|---|---|---|
| 0 s | request sent to the supplier | request sent to the supplier |
| 1 s | still waiting, thread busy | timeout: ResourceAccessException |
| 1 s | still waiting, thread busy | the Shop API answers 503; the thread is free |
| 3 s | the supplier answers at last | (long done) |
:::
:::

:::step{type=task task=handle_supplier_errors title="Your turn: not stocked, down, or too slow"}
Three changes:

1. In **`SupplierClient.available`**: when the supplier answers **404**, return **0**.
2. In **`SupplierClient`'s constructor**: give the client a **1 second** read timeout (and a connect timeout), with
   a `SimpleClientHttpRequestFactory`.
3. In **`SupplierController`**: when the client throws a **`RestClientException`** (supplier down or too slow), answer
   **503** instead of 500.

Rebuild, restart the Shop API, and try all three cases:

```bash run
curl -i localhost:8080/supplier-stock/MISSING; echo; curl -i -w "\ntook %{time_total}s\n" localhost:8080/supplier-stock/SLOW
```

`200` with `"available":0`, then `503` after about **1 second**, not 3 (on our lab machine: `took 1.004898s`).
Finally, stop the supplier (Ctrl+C in Terminal 1) and ask for kulfi: still a calm `503`,
`{"sku":"KUL-1","error":"Supplier unavailable"}`. All three answers are what our lab machine gave. Press **Check**.

Usual slips: the timeout factory created but not passed to the builder (`.requestFactory(factory)` is easy to
forget; the slow call then still takes 3 seconds), catching `HttpClientErrorException` in the controller instead of
`RestClientException` (a timeout is not a client error, so it still becomes a 500), or returning 0 for *every*
error (then "supplier down" looks like "out of stock").
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which exception does RestClient throw when the read timeout passes?
:::
- [ ] HttpServerErrorException
- [x] ResourceAccessException
- [ ] TimeoutException
:::explain
Network problems, refused connections and timeouts are `ResourceAccessException`. Status codes from the other side
are `HttpClientErrorException` (4xx) and `HttpServerErrorException` (5xx).
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why is 503 better than 500 when the supplier is down?
:::
- [x] 503 says the problem is temporary and outside this service; clients and load balancers may retry later
- [ ] 503 is faster to send
- [ ] 500 cannot have a body
:::explain
500 means "this service has a bug". 503 means "this service is fine, but cannot do this right now".
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Without timeouts, a supplier starts taking 60 seconds per answer. What happens to `GET /products`, which never calls the supplier?
:::
- [ ] Nothing: it does not use the supplier
- [x] It slows down or stops too, once every worker thread is stuck waiting on the supplier
- [ ] It answers 503
:::explain
Threads are shared. When enough requests wait on the slow supplier, none are left for anything else. Timeouts
protect the whole app, not just one endpoint.
:::
:::

:::step{type=deep-dive title="Go deeper: retries, circuit breakers, and declarative clients"}
**Retries.** A short glitch often succeeds on a second try. Retry with a growing wait (1s, 2s, 4s), a few times at
most, and only for requests that are safe to repeat (GET, or calls with an idempotency key, chapter 30).

**Circuit breakers.** If a service keeps failing, stop calling it for a while and answer at once instead: a
**circuit breaker** (Resilience4j) "opens" after repeated failures and "closes" again when the service recovers.
It stops you from hammering a struggling service.

**HTTP interfaces.** Spring 6 can write the client for you: declare an interface with
`@GetExchange("/stock/{sku}") SupplierStock stock(@PathVariable String sku);` and Spring builds the implementation,
much like Spring Data builds repositories.

**Testing clients.** The hidden check for this chapter starts its own fake supplier inside the test (with
`@DynamicPropertySource` to point `supplier.base-url` at it). WireMock is a popular library for exactly that.
:::

:::step{type=recap title="What you can do now"}
You can now call other services safely:

- Your app can be a **client**: `RestClient` from Spring Boot's `RestClient.Builder`, with the base URL as a setting.
- `http.get().uri("/path/{x}", x).retrieve().body(Type.class)` reads the answer into a record.
- Failures are exceptions: 4xx `HttpClientErrorException`, 5xx `HttpServerErrorException`, no answer
  `ResourceAccessException`, all `RestClientException`s. Decide what each answer **means** for you (404 = 0 here).
- **Always set timeouts**; one slow dependency can otherwise use up every thread.
- A failing dependency becomes a fast **503** from your API.

:::photo{src="/lesson-images/spring/spring-29-notes.webp" alt="Sketchnote: Calling other services. Your app becomes a client, and every answer needs a meaning. Flow: RestClient GET, the supplier answers or not, you decide what each answer means, too slow gives a fast 503. Remember: the base URL is a setting; 4xx, 5xx and no answer become exceptions; always set timeouts; a failing dependency becomes a fast 503." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 30, the capstone: a complete checkout, built by you, using everything from this course.
:::
