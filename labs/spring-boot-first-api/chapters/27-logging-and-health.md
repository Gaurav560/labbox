:::step{type=story title="Seeing a server you cannot see"}
On your laptop, you watch the app in a terminal. On a production server, nobody watches anything. The app runs on
a machine you may never log into, maybe ten copies of it behind a load balancer, serving customers at 3 a.m. When a
customer says "my order failed", you have two ways to find out what happened: the app's **logs**, and its
**health**.

:::photo{src="/lesson-images/spring/cern-server-room.webp" alt="A large server room at CERN: long rows of metal racks under bright ceiling lights, with no person in sight" credit="Florian Hirzinger" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:CERN_Server_03.jpg"}
A server room at CERN. Rows of machines, and nobody watching a terminal: logs and health checks are how you see inside.
:::

Spring Boot has both built in. Logging, through **SLF4J** and **Logback**, writes structured, filterable log lines.
**Actuator**, which you added in chapter 2, exposes operational endpoints like `/actuator/health`. This chapter
teaches you to use both the way production teams do.

:::mission
Replace a `System.out.println` with a proper WARN log line, and expose the health and info endpoints.
:::
:::

:::step{type=concept title="Why not System.out.println?"}
The word **log** comes from the sea. Sailors measured a ship's speed by throwing a wooden log overboard on a knotted
rope, and wrote the result, with the time, in the ship's **log book**. Every app's log is that book: what happened,
and when.

:::photo{src="/lesson-images/spring/ships-log.webp" alt="The cloth-bound log book of the ship Belgica from the Belgian Antarctic Expedition of 1897, with a label on the cover" credit="Till.niermann" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Belgica_Ship%27s_log.jpg"}
The log book of the Belgica, Antarctic expedition, 1897.
:::

`System.out.println("out of stock " + sku)` writes one bare line. Compare it with a line from a **logger**:

```text
2026-11-21T12:20:36.011Z  WARN 142 --- [shop-api] [nio-8082-exec-2] com.shop.stock.StockService : Out of stock: SAM-1
```

Every part of it is useful:

- **When**: an exact timestamp, so you can match it with the customer's "at 14:02".
- **How serious**: the **level**, `WARN`.
- **Which app** (`[shop-api]`, your `spring.application.name` from chapter 0), and which process (`142`).
- **Which thread**: `nio-8082-exec-2`, a Tomcat request thread (chapter 10). All lines of one request share it.
- **Which class** wrote it: `com.shop.stock.StockService`.
- **The message**.

And because every line has a level, you can **choose** what to keep: everything on your laptop, only warnings and
errors in production, and an alert to your phone for every `ERROR`. `println` has none of that: no level, no time,
no class, and no way to switch it off.

:::

:::step{type=concept title="Log levels"}
There are five levels, from the chattiest to the most serious:

- **TRACE**: extremely detailed, step-by-step internals. You saw Spring's TRACE log in chapter 10.
- **DEBUG**: details useful while developing or investigating ("loaded 3 prices", "cache miss for LAS-1").
- **INFO**: normal, important events ("Started ShopApiApplication", "order 4711 placed").
- **WARN**: something unusual that the app handled, but someone may want to know ("out of stock", "retrying a
  slow supplier").
- **ERROR**: something failed and needs attention ("payment provider unreachable", an unexpected exception).

You set a **threshold** per package; only that level and the more serious ones are written. Spring Boot's
default is `INFO`. In `application.properties`:

```properties
logging.level.com.shop=DEBUG                # everything from your code, DEBUG and up
logging.level.org.hibernate.SQL=DEBUG       # Hibernate's SQL statements (like show-sql, but through the logger)
logging.level.root=WARN                     # everything else: only WARN and ERROR
```

Choosing the right level is a skill. A good rule: in production, **INFO** should tell the story of what happened,
**WARN** should be rare enough that someone reads them, and **ERROR** should always mean someone must act.
:::

:::step{type=example title="Worked example: logging from a class"}
```java
@Service
public class PaymentService {

    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

    public void charge(String orderId, int paise) {
        log.info("Charging order {} for {} paise", orderId, paise);
        if (paise > 1_000_000) {
            log.warn("Large payment for order {}", orderId);
        }
    }
}
```

- **`Logger`** and **`LoggerFactory`** come from **`org.slf4j`**. SLF4J is the logging *interface* every Java
  library agrees on; **Logback** (from the starter, chapter 2) is the library that actually writes the lines.
- One logger per class, **`private static final`**, created with the class itself, so every line names its source.
- **`{}` placeholders**: SLF4J fills them from the arguments, in order. And it only builds the text **if the line
  will actually be written**, so a `DEBUG` line costs almost nothing when DEBUG is off. Never write
  `log.debug("total " + total)`: the `+` builds the string every time, even when the line is thrown away.
- To log an exception with its stack trace, pass it as the **last** argument: `log.error("Payment failed for {}",
  orderId, e)`.
:::

:::step{type=try title="Find the println" file="27-logging-and-health/src/main/java/com/shop/stock/StockService.java" line="13-20"}
`StockService.take`, on the right, prints with `System.out.println` when an item is out of stock. Start the app and
trigger it (the samosa stock starts at 0):

```bash run
cd 27-logging-and-health && mvn -q -o package -DskipTests && java -jar target/logging-and-health.jar
```

```bash run
curl -X POST localhost:8080/stock/SAM-1/take
```

Look at Terminal 1. Between the neat log lines, there is a bare one:

```text
out of stock SAM-1
```

No time, no level, no class. On a server producing thousands of lines a minute, nobody would ever find it, and no
alert could ever be set on it.
:::

:::step{type=task task=log_warning title="Your turn: a proper WARN line"}
In `StockService`:

1. Add a logger for the class: `private static final Logger log = LoggerFactory.getLogger(StockService.class);`
   (imports `org.slf4j.Logger` and `org.slf4j.LoggerFactory`).
2. Replace the `println` with a **WARN** line, `Out of stock: <sku>`, using a `{}` placeholder for the sku.

Rebuild, run, take a samosa again, and look at the log:

```text
WARN 142 --- [shop-api] [nio-8080-exec-2] com.shop.stock.StockService : Out of stock: SAM-1
```

Press **Check**.
:::

:::step{type=concept title="Actuator: is the app healthy?"}
A load balancer sits in front of your app's copies and spreads requests between them. It needs to know, every few
seconds, which copies are **healthy**, so it stops sending customers to a broken one. Kubernetes does the same to
decide when to restart a container. They ask the app itself, at **`/actuator/health`**.

:::diagram{name="actuator-endpoints"}
The load balancer calls health; people and dashboards read info and metrics.
:::

- **`/actuator/health`** answers `{"status":"UP"}` (with 200) when the app works, and `{"status":"DOWN"}` (with
  **503**) when it does not. Spring Boot adds a check for each thing the app depends on: with a database, the
  health includes "can I reach the database?". One part DOWN makes the whole status DOWN.
- **`/actuator/info`** shows facts you choose: app name, version, git commit, so you know exactly what is running.
- **`/actuator/metrics`** gives numbers: request counts and times, memory, database connections.

By default, only **health** is reachable over HTTP. The others can reveal internal details, so you expose them on
purpose. The log tells you how many are exposed:

```text
o.s.b.a.e.web.EndpointLinksResolver : Exposing 1 endpoint beneath base path '/actuator'
```
:::

:::step{type=example title="Worked example: exposing and filling info"}
Exposure is a setting:

```properties
management.endpoints.web.exposure.include=health,info
```

The info endpoint is empty until something fills it. The simplest source is your own settings: switch on the
**env** contributor, and every property starting with `info.` appears in it:

```properties
management.info.env.enabled=true
info.app.name=Payments API
info.app.team=checkout
```

```bash
curl -s localhost:8080/actuator/info
{"app":{"name":"Payments API","team":"checkout"}}
```

`info.app.name` became the nested JSON `{"app":{"name":...}}`. (Remember chapter 8? These settings switch
auto-configured features on and off through conditions, just like ShopKit's festival banner.)
:::

:::step{type=task task=health_info title="Your turn: expose health and info"}
In `27-logging-and-health/src/main/resources/application.properties`:

1. expose **`health`** and **`info`** over HTTP;
2. switch on the **env** info contributor;
3. set **`info.app.name`** to `Shop API`.

Rebuild, run, and look at all three:

```bash run
curl localhost:8080/actuator/health; echo; curl localhost:8080/actuator/info; echo; curl localhost:8080/actuator
```

```text
{"status":"UP"}
{"app":{"name":"Shop API"}}
{"_links":{"self":...,"health":...,"info":...}}
```

`/actuator` on its own lists every exposed endpoint, and the start-up log now says `Exposing 2 endpoints`. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Production runs with the INFO threshold. Which lines are written?
:::
- [ ] Only ERROR
- [x] INFO, WARN and ERROR
- [ ] All of them, including DEBUG
:::explain
A threshold writes its own level and everything more serious. DEBUG and TRACE are skipped (and, with
placeholders, cost almost nothing).
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
The database goes down. What does /actuator/health answer?
:::
- [ ] 200 UP: the app itself still runs
- [x] 503 DOWN: the database check fails, so the whole status is DOWN
- [ ] Nothing: the endpoint stops
:::explain
Each dependency adds its own check. One DOWN makes the status DOWN, and the load balancer stops sending customers
to this copy.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why is `log.debug("total {}", total)` better than `log.debug("total " + total)`?
:::
- [ ] It prints more nicely
- [x] With {}, the text is only built if the line is actually written
- [ ] The + version does not compile
:::explain
With `+`, Java builds the string before calling `debug`, even when DEBUG is off and the line is thrown away. In a
loop running a million times, that adds up.
:::
:::

:::step{type=deep-dive title="Go deeper: JSON logs, metrics, request ids, and DevTools"}
**Logs as JSON.** Log systems (ELK, Loki, Datadog) search logs by field. Spring Boot 3.4 can write each line as a
JSON object: `logging.structured.format.console=ecs`.

**Request ids in every line.** Put chapter 18's request id into SLF4J's **MDC** in the filter, add it to the log
pattern, and every line of a request carries it: one search finds a request's whole story.

**Metrics.** With the Micrometer Prometheus registry, `/actuator/prometheus` serves every metric for Prometheus and
Grafana dashboards: requests per second, the slowest endpoints, database pool usage.

**Health groups.** Kubernetes separates "alive" from "ready for traffic": Spring Boot offers
`/actuator/health/liveness` and `/actuator/health/readiness` for exactly that.

**DevTools.** While developing, `spring-boot-devtools` restarts the app automatically when you rebuild, so you stop
pressing Ctrl+C after every change. It switches itself off in a packaged production jar.
:::

:::step{type=recap title="What you can do now"}
You can now see what a running app is doing:

- Use an **SLF4J `Logger`** (`LoggerFactory.getLogger(YourClass.class)`), never `System.out.println`.
- **Levels**: TRACE, DEBUG, INFO, WARN, ERROR; set thresholds per package with `logging.level.<package>=...`.
- **`{}` placeholders** build text only when the line is written; pass exceptions as the last argument.
- **Actuator**: `/actuator/health` (UP 200 / DOWN 503, for load balancers), `/actuator/info` (facts you choose),
  `/actuator/metrics`. Expose them on purpose with `management.endpoints.web.exposure.include`.
- `management.info.env.enabled=true` + `info.*` properties fill the info endpoint.

:::photo{src="/lesson-images/spring/spring-27-notes.webp" alt="Handwritten notes about Logging and health: Logger, never System.out, TRACE DEBUG INFO WARN ERROR, curly-brace placeholders, /actuator/health: UP or DOWN, /actuator/info" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 28: right now anyone can call any endpoint. Security.
:::
