:::step{type=story title="Code that runs for every request"}
Some jobs belong to *every* request, not to one endpoint. Give each request an id so it can be traced
through the logs. Check that the caller is logged in. Measure how long requests take. Add a header to every
answer.

You could copy those lines into every controller method. You would forget one, and then change them in
thirty places when the rules change. Spring gives you two proper places for "do this around every request":
**filters** and **interceptors**. They sit at different points in the journey you learned in chapter 10,
and choosing the right one is part of the skill.

:::mission
Give every request an id with a filter, and tag every API response with the Java method that handled it,
using an interceptor.
:::
:::

:::step{type=concept title="Where they sit in the journey"}
Recall the journey of a request from chapter 10: Tomcat, then the DispatcherServlet, then the handler
mapping, then your method. Filters and interceptors hook in at two different places:

```text
Tomcat
  -> Filter 1 -> Filter 2 -> ...            filters: before Spring MVC, for EVERY request
       -> DispatcherServlet
            -> handler mapping (finds your method)
            -> Interceptor.preHandle         interceptors: Spring MVC knows the method now
                 -> your controller method
            <- Interceptor.postHandle / afterCompletion
       <-
  <- the filters again, on the way out
```

- A **filter** is part of the Java web standard (Jakarta Servlet), not specific to Spring MVC. It sees
  **every** request, even ones for paths no controller handles, and it runs **before** Spring has decided
  anything. It works with the raw request and response.
- An **interceptor** is part of Spring MVC. It runs **after** the handler mapping, so it knows **which
  controller method** will handle the request. And you choose which paths it applies to.

A rule of thumb: if the job does not care which endpoint it is (ids, security checks, compression, logging
every hit), use a filter. If it needs to know the controller method, or only applies to some paths, use an
interceptor.
:::

:::step{type=concept title="A filter, and the chain" file="18-filters-and-interceptors/src/main/java/com/shop/web/RequestIdFilter.java" line="14-24"}
`RequestIdFilter` is on the right. It extends **`OncePerRequestFilter`**, a small Spring base class that
guarantees the filter runs exactly once per request (in some special cases, like error pages, a plain
filter could run twice). You write one method:

```java
protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
```

- `request` is the incoming request: you can read its path, headers and parameters.
- `response` is the response being built: you can set headers and the status.
- `chain` is **everything after this filter**: the other filters, then Spring MVC, then your controller.

The most important line in any filter is:

```java
chain.doFilter(request, response);
```

It means "pass the request on". Whatever you write **before** it runs on the way **in**; whatever you write
**after** it runs on the way **out**, when the controller has finished. If a filter does not call it, the
request stops right there: nothing after the filter runs. That is how a security filter refuses a request:
it sets 401 and simply does not pass it on.

Because it is a `@Component`, Spring Boot registers it automatically for every request.
:::

:::step{type=concept title="Why a request id?"}
Imagine a customer calls: "my order failed at 14:02". Your server handles hundreds of requests a minute,
and in a real system one order passes through several services (orders, payments, stock), each writing its
own logs. How do you find the lines that belong to *that* request?

You give every request an **id** when it arrives, return it in the response (so the customer's app can
show it, or a support person can ask for it), write it in every log line, and pass it on to the next
service in a header. Then one search for that id finds the request's whole story, across all services.

The common header name is **`X-Request-Id`**. The rule is: if the request already has one (because a
service in front of you assigned it), keep it; otherwise make a new one. That way the id stays the same
along the whole path.

A good unique id is a **UUID** (Universally Unique Identifier), a 128-bit random value written like
`d394ce8a-1b66-43e5-b9ac-338c6f61910f`. Java makes one with `UUID.randomUUID().toString()`. The chance of
two being equal is so small it can be ignored.
:::

:::step{type=task task=request_id_filter title="Your turn: the request id filter"}
In `RequestIdFilter.doFilterInternal`, before `chain.doFilter(...)`:

1. Read the request's `X-Request-Id` header (`request.getHeader("X-Request-Id")`).
2. If it is `null` or blank, make a new id with `UUID.randomUUID().toString()` (import `java.util.UUID`).
3. Set it on the response: `response.setHeader("X-Request-Id", id)`.

Build, run, and look at the headers:

```bash run
cd 18-filters-and-interceptors && mvn -q -o package -DskipTests && java -jar target/filters.jar
```

```bash run
curl -i localhost:8080/api/products; echo; curl -i localhost:8080/ping; echo; curl -i -H "X-Request-Id: order-42" localhost:8080/api/products
```

Each response has an `X-Request-Id`: a fresh UUID for the first two (even `/ping`: filters see every request), and
`order-42` for the third, which sent its own. That is what our lab machine answered. Press **Check**.

Usual slips: setting the header *after* `chain.doFilter` (by then the controller may already have sent the
response, so the header can come too late), testing only for `null` and not for blank (a header sent as
`X-Request-Id:` with nothing after it is blank), or removing the `chain.doFilter` line (then every request stops in
the filter).
:::

:::step{type=concept title="An interceptor" file="18-filters-and-interceptors/src/main/java/com/shop/web/HandledByInterceptor.java" line="9-20"}
Now `HandledByInterceptor.java`. An interceptor implements **`HandlerInterceptor`**, which has three
methods you can override, for three moments:

- **`preHandle`**: just before the controller method. Return `true` to continue, `false` to stop the request.
- **`postHandle`**: after the controller method, before the response is finished. (For REST controllers the
  body is usually already written by then, so it is less useful.)
- **`afterCompletion`**: after everything, even when an exception happened. Good for timing and cleanup.

Look at the third argument of `preHandle`: `Object handler`. For a normal endpoint, it is a
**`HandlerMethod`**, which describes the controller method Spring chose: its class, its name, its
parameters, even its annotations. A filter can never see this; an interceptor can. This one uses it to add
a header naming the method:

```text
X-Handled-By: ProductController#all
```

This interceptor is finished already. But it does nothing yet, because an interceptor must be
**registered**: Spring MVC needs to be told to use it, and for which paths.
:::

:::step{type=example title="Worked example: registering an interceptor"}
You register interceptors in a configuration class that implements **`WebMvcConfigurer`**, Spring MVC's
customisation interface. It has many methods with empty defaults; you override the ones you need:

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final AuditInterceptor audit;

    public WebConfig(AuditInterceptor audit) {
        this.audit = audit;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(audit)
                .addPathPatterns("/admin/**")          // only these paths...
                .excludePathPatterns("/admin/health");  // ...except this one
    }
}
```

- The interceptor is a bean, injected through the constructor like any other.
- **`addInterceptors`** is called by Spring once, at start-up, with a **registry** to add to.
- **`addPathPatterns`** limits it to some paths. `/**` means "anything below, at any depth": `/admin/**`
  matches `/admin/users` and `/admin/users/7/orders`, but not `/products`.
:::

:::step{type=task task=handled_by_interceptor title="Your turn: register the interceptor for the API"}
`WebConfig.java` already receives the `HandledByInterceptor`. Override **`addInterceptors`** and register
it for the API's paths only: **`/api/**`**. `/ping` is not part of the API, so it must not get the header.
(Import `org.springframework.web.servlet.config.annotation.InterceptorRegistry`.)

Rebuild, run, and compare:

```bash run
curl -i localhost:8080/api/products; echo; curl -i localhost:8080/ping
```

On our lab machine:

```text
HTTP/1.1 200
X-Request-Id: aea03228-7934-4a3c-9b46-da94bbe09db4
X-Handled-By: ProductController#all
Content-Type: application/json

["Mango kulfi","Samosa","Fruit custard"]

HTTP/1.1 200
X-Request-Id: 7418b4f0-cb5f-455f-9aac-0aaf26d43abb
Content-Type: text/plain;charset=UTF-8
Content-Length: 4

pong
```

The API response has both headers; `/ping` only has the filter's. (Your UUIDs will differ: they are random.) Press
**Check**.

Usual slips: the pattern `/api/*` (one `*` matches only one level, so `/api/products/7` would be left out), or
forgetting `@Override` and misspelling the method name (then Spring never calls it, and nothing is registered).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In this chapter's app (the interceptor registered for `/api/**`), a request comes in for `/nothing-here`. Which runs?
:::
- [ ] The filter and the interceptor
- [x] Only the filter: `/nothing-here` is outside the interceptor's paths
- [ ] Neither
:::explain
Filters run for every request, mapped or not. The interceptor only runs for the paths it was registered for. (On
our lab machine, `/nothing-here` answered 404 with an `X-Request-Id` and no `X-Handled-By`. We also tried the
interceptor registered for every path, `/**`: then it *did* run, and named `BasicErrorController#error`, because
Spring Boot answers a 404 by passing the request on to its own error controller, which is a handler too.)
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A filter forgets to call `chain.doFilter(request, response)`. What does the client get?
:::
- [ ] The normal response; Spring calls the chain anyway
- [x] Whatever the filter wrote, usually an empty 200: the controller never runs
- [ ] A 500 error
:::explain
The chain *is* the rest of the request. Not calling it stops the request at that filter. That is exactly
what a security filter does on purpose, after setting a 401.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
You want to log how long each controller method takes, with the method's name. Filter or interceptor?
:::
- [ ] Filter
- [x] Interceptor: it knows the HandlerMethod
- [ ] Neither can do that
:::explain
A filter can time the whole request, but only an interceptor knows which controller method handled it:
record the start in `preHandle`, log in `afterCompletion`.
:::
:::

:::step{type=deep-dive title="Go deeper: filter order, MDC, and when to use which"}
**Order.** Several filters run in a chain; `@Order(1)` (lower first) on a filter sets its place. Spring
Security (chapter 28) is itself a chain of filters, placed near the front.

**The id in every log line.** Put the request id in the **MDC** (`MDC.put("requestId", id)`, from SLF4J) at
the start of the filter and remove it in a `finally` block after `chain.doFilter`. Then every log line
written during that request can include it automatically, with a small change to the log pattern. That is
how the id really becomes searchable.

**Other options.** For logic about one controller's methods, Spring also offers `@ControllerAdvice`
(chapter 17, for errors) and aspects (AOP), which wrap any bean's methods. Filters and interceptors are
the right tools for web-request-wide concerns.
:::

:::step{type=recap title="What you can do now"}
You can now run code around every request:

- **Filters** (Jakarta Servlet, `OncePerRequestFilter`) run before Spring MVC for **every** request.
  `chain.doFilter(...)` passes the request on; code before it runs on the way in, after it on the way out;
  not calling it stops the request.
- **Interceptors** (`HandlerInterceptor`) run around the controller method and know it (`HandlerMethod`).
  `preHandle`, `postHandle`, `afterCompletion`.
- Register interceptors in a **`WebMvcConfigurer`**'s `addInterceptors`, with `addPathPatterns` to choose
  paths (`/api/**`).
- A **request id** (`X-Request-Id`, a UUID, or the caller's own) lets you follow one request through
  every log and service.

:::photo{src="/lesson-images/spring/spring-18-notes.webp" alt="Sketchnote: Filters and interceptors. Code that runs around requests, without copying it into every endpoint. Flow: filter, DispatcherServlet, interceptor preHandle, your method, interceptor afterCompletion. Remember: a filter sees every request, before Spring MVC; chain.doFilter passes the request on; an interceptor knows the controller method and only runs on its registered paths; X-Request-Id gives one id to find one request's logs." ai="true"}
One page of notes for this chapter.
:::

That completes Part 2: you can build a complete, well-behaved REST API. Part 3 gives it a real database,
starting with chapter 19.
:::
