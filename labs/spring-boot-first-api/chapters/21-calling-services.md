:::step{type=story title="Why this chapter"}
A backend rarely works alone. The Shop API asks a supplier how much stock it has, a payment provider
whether a card was charged, a courier when a parcel will arrive. Each of those calls goes over the
network, and the network can be slow, or the other side can be down. This chapter calls another service
with Spring's `RestClient`, and handles the ways it can fail.

:::mission
In the `21-calling-services` folder: read the supplier's stock over HTTP, treat "not stocked" as 0, and
answer 503 quickly when the supplier is too slow.
:::
:::

:::step{type=concept title="RestClient"}
`RestClient` (Spring Framework 6.1 and later) is Spring's HTTP client with a fluent API. Spring Boot
provides a `RestClient.Builder` bean, already set up with the same JSON handling as your controllers:

```java
RestClient http = builder.baseUrl("https://supplier.example").build();

SupplierStock s = http.get()
        .uri("/stock/{sku}", "TEA-1")
        .retrieve()
        .body(SupplierStock.class);
```

`retrieve()` sends the request; `body(...)` reads the JSON answer into a class or record, the same way
`@RequestBody` does in a controller. A 4xx answer throws `HttpClientErrorException`, a 5xx answer
`HttpServerErrorException`, and a network problem or timeout `ResourceAccessException`. All of them are
`RestClientException`s.

:::diagram{name="service-call"}
The shop waits for the supplier; a timeout limits how long.
:::
:::

:::step{type=example title="Worked example: a weather client"}
```java
@Component
public class WeatherClient {

    public record Forecast(String city, int celsius) {
    }

    private final RestClient http;

    public WeatherClient(RestClient.Builder builder, @Value("${weather.base-url}") String baseUrl) {
        this.http = builder.baseUrl(baseUrl).build();
    }

    public Optional<Forecast> today(String city) {
        try {
            return Optional.ofNullable(http.get().uri("/today/{city}", city).retrieve().body(Forecast.class));
        } catch (HttpClientErrorException.NotFound e) {
            return Optional.empty();
        }
    }
}
```

The base URL is a property, so tests and production can point to different servers. A 404 here means "no
such city", an expected answer, so it becomes `Optional.empty()` instead of an error.
:::

:::step{type=task task=fetch_stock title="Read the supplier's stock"}
In `21-calling-services/.../supplier/SupplierClient.java`, make `available(sku)` call
`GET /stock/{sku}` on the supplier, read the JSON into `SupplierStock`, and return `available`.
:::

:::step{type=concept title="Timeouts: never wait forever"}
Without a timeout, a request to a supplier that has stopped answering can wait for minutes. Each waiting
request holds one of the server's threads (about 200 in Tomcat by default). When enough requests wait,
the shop stops answering **everyone**, even requests that never call the supplier. One slow service has
brought down another.

A **read timeout** limits how long to wait for an answer:

```java
SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
factory.setConnectTimeout(Duration.ofSeconds(1));
factory.setReadTimeout(Duration.ofSeconds(1));
RestClient http = builder.baseUrl(baseUrl).requestFactory(factory).build();
```

When the time is up, the call throws `ResourceAccessException`. Your API then answers fast with
**503 Service Unavailable**: "I am fine, but something I need is not".

:::trace{title="GET /supplier-stock/SLOW, with and without a timeout"}
| time | no timeout | 1 second read timeout |
|---|---|---|
| 0 s | request sent to the supplier | request sent to the supplier |
| 1 s | still waiting | timeout: ResourceAccessException |
| 1 s | still waiting | the shop answers 503 |
| 3 s | the supplier answers; the thread was held 3 s | (the thread is already free) |
:::
:::

:::step{type=predict title="Guess first"}
:::question
The supplier answers 404 for an item it does not stock. Without any try/catch, what does `GET /supplier-stock/MISSING` return to your client?
:::
- [ ] 404, passed through
- [x] 500: HttpClientErrorException is not handled, so Spring answers with a server error
- [ ] 200 with available 0
:::explain
An unhandled exception in a controller becomes 500. Decide what each answer from the other service means
for your API, and handle it.
:::
:::

:::step{type=try title="Call the shop"}
The `supplier.base-url` points to a port where nothing listens, so the call fails. Start the app and see
what your API answers:

```bash run
cd 21-calling-services && mvn -q -o package -DskipTests && java -jar target/calling-services.jar
```

```bash run
curl -s -w "\n%{http_code}\n" localhost:8080/supplier-stock/TEA-1
```
:::

:::step{type=task task=handle_supplier_errors title="Handle the supplier's failures"}
Three changes:

- in `SupplierClient`, a 404 from the supplier returns 0 (not stocked);
- in `SupplierClient`, give the client a read timeout of 1 second;
- in `SupplierController`, a `RestClientException` (supplier down or too slow) answers 503.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which exception does RestClient throw when the read timeout passes?
:::
- [ ] HttpServerErrorException
- [x] ResourceAccessException
- [ ] TimeoutException
:::explain
Network problems, refused connections and timeouts are all `ResourceAccessException`. Status codes from
the other side are `HttpClientErrorException` (4xx) and `HttpServerErrorException` (5xx).
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
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

:::step{type=deep-dive title="Retries, circuit breakers, and declarative clients"}
A timeout limits one call. **Retries** (with a growing wait between them) handle short glitches, but only
for requests that are safe to repeat. A **circuit breaker** (Resilience4j) stops calling a service that
keeps failing for a while, and answers at once instead. Spring 6 also has **HTTP interfaces**: declare a
Java interface with `@GetExchange("/stock/{sku}")` and Spring builds the client for you. The "Spring Boot
in production" course builds all three.
:::

:::step{type=recap title="Chapter done"}
- `RestClient` sends requests and reads JSON into records, like a controller in reverse.
- 4xx, 5xx and network failures throw different `RestClientException`s; decide what each means.
- Always set a timeout on calls to other services.
- A dependency that fails becomes 503 from your API, quickly.
:::
