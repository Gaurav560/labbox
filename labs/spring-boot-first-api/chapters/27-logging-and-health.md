:::step{type=story title="Why this chapter"}
Once the API runs on a server, you cannot watch it in a terminal. You need two things: **logs** that
tell you what happened, and a **health endpoint** that tells a load balancer (and you) whether the app is
working. Spring Boot has both built in: SLF4J with Logback for logs, and **Actuator** for health and
information.

:::mission
In the `27-logging-and-health` folder: expose the health and info endpoints, and replace a
`System.out.println` with a proper WARN log line.
:::
:::

:::step{type=concept title="Why not System.out.println"}
`System.out.println` writes a bare line. A log line from a logger carries more:

```text
2026-11-21T10:15:02.114Z  WARN 4211 --- [shop-api] [nio-8080-exec-3] c.shop.stock.StockService : Out of stock: SAM-1
```

The time, the **level** (`WARN`), the process, the thread and the class that logged it. With levels you
can choose what to keep: `DEBUG` while developing, `INFO` and above in production, and alerts on `ERROR`.
The levels from least to most serious: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`.
:::

:::step{type=example title="Worked example: logging in a service"}
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

`Logger` and `LoggerFactory` come from `org.slf4j`. The `{}` placeholders are filled from the arguments,
and only when the line is actually written, so a disabled `DEBUG` line costs almost nothing. Never
build the message with `+` inside a log call.

You set levels in `application.properties`:

```properties
logging.level.com.shop=DEBUG
logging.level.org.hibernate.SQL=DEBUG
```
:::

:::step{type=task task=log_warning title="Log the out-of-stock warning"}
In `27-logging-and-health/.../stock/StockService.java`, replace the `System.out.println` with a WARN log
line `Out of stock: <sku>`, using an SLF4J `Logger` for `StockService`.
:::

:::step{type=concept title="Actuator: health and info"}
`spring-boot-starter-actuator` adds operational endpoints under `/actuator`:

- **`/actuator/health`** answers `{"status": "UP"}` when the app and what it depends on (the database,
  for example) are working, and `DOWN` with status 503 when they are not. Load balancers and Kubernetes
  call it to decide whether to send traffic to this instance.
- **`/actuator/info`** shows facts you choose: the app name, its version, the git commit.

Only `health` is reachable over HTTP by default, because the others can reveal internal details. You
choose what to expose:

```properties
management.endpoints.web.exposure.include=health,info
```

:::diagram{name="actuator-endpoints"}
The load balancer calls health; people and dashboards read info and metrics.
:::
:::

:::step{type=example title="Worked example: filling /actuator/info"}
With the **env** contributor turned on, every property that starts with `info.` appears in the info endpoint:

```properties
management.info.env.enabled=true
info.app.name=Payments API
info.app.team=checkout
```

```bash
curl -s localhost:8080/actuator/info
{"app":{"name":"Payments API","team":"checkout"}}
```
:::

:::step{type=predict title="Guess first"}
:::question
You add Actuator and call `GET /actuator/info` without changing any property. What do you get?
:::
- [ ] {} with 200
- [x] 404: info is not exposed over HTTP by default
- [ ] 401: Actuator needs a login
:::explain
Only health is exposed by default. Every other endpoint must be listed in `management.endpoints.web.exposure.include`.
:::
:::

:::step{type=try title="Ask the app how it is"}
```bash run
cd 27-logging-and-health && mvn -q -o package -DskipTests && java -jar target/logging-and-health.jar
```

In a second tab:

```bash run
curl -s localhost:8080/actuator/health; echo; curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/actuator/info
```
:::

:::step{type=task task=health_info title="Expose health and info"}
In `27-logging-and-health/src/main/resources/application.properties`: expose `health` and `info` over
HTTP, turn on the env info contributor, and set `info.app.name` to `Shop API`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Production runs with `logging.level.root=INFO`. Which of these lines are written?
:::
- [ ] Only ERROR
- [x] INFO, WARN and ERROR
- [ ] All of them, including DEBUG
:::explain
A level writes itself and everything more serious. DEBUG and TRACE are skipped.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The database goes down. What does `/actuator/health` answer?
:::
- [ ] 200 UP: the app itself still runs
- [x] 503 DOWN: the database health check fails
- [ ] Nothing: the endpoint stops
:::explain
Spring Boot adds a health check for each thing it connects to. One DOWN makes the whole status DOWN, so
the load balancer stops sending traffic to this instance.
:::
:::

:::step{type=deep-dive title="Metrics, and logs as JSON"}
Actuator also has `/actuator/metrics` (request counts and times, memory, database pool), and with
Micrometer it exports them to Prometheus at `/actuator/prometheus`. In production, logs usually go out
as JSON, one object per line, so a log system can search by field: Spring Boot 3.4 does this with
`logging.structured.format.console=ecs`. The "Spring Boot in production" course goes deep on both.
:::

:::step{type=recap title="Chapter done"}
- Use an SLF4J `Logger`, with `{}` placeholders, not `System.out.println`.
- Levels: TRACE, DEBUG, INFO, WARN, ERROR; set them per package in properties.
- Actuator's `/actuator/health` is for load balancers; `/actuator/info` shows facts you choose.
- Expose endpoints over HTTP on purpose, with `management.endpoints.web.exposure.include`.
:::
