:::step{type=story title="Part 2: building REST APIs"}
Welcome to Part 2. In Part 1 you learned what Spring is doing underneath everything: the container, beans,
configuration, auto-configuration. From now on, we build the Shop API's real REST endpoints: reading
requests, accepting JSON, answering with the right status codes, validating input and handling errors.

The word **REST** (Representational State Transfer) comes from this man's PhD thesis. In 2000, **Roy Fielding**,
one of the authors of the HTTP standard itself, described the style the web works best in: resources with addresses, a few standard methods, and
status codes that mean the same thing everywhere. Part 2 is that style, in Spring.

:::photo{src="/lesson-images/spring/fielding.webp" alt="Roy Fielding, a man with curly brown hair in a light shirt, speaking at a lectern on a dark stage" credit="Phil Whitehouse" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:Roy_Fielding_(cropped).jpg"}
Roy Fielding, who named and described REST in 2000: the style every endpoint in Part 2 follows.
:::

Before writing more endpoints, it pays to know precisely what happens to **one request** inside Spring.
You have written `@GetMapping` methods since chapter 3, and they just worked. But who decided that your
method should run? How did a `List` become JSON? Why do you sometimes get 404, sometimes 405, sometimes
406? This chapter follows a single request through Spring, step by step, and you will watch Spring's own
log describe each step as it happens.

:::mission
Follow a request through Spring MVC, move the cart API under `/api/v1`, and handle a second method on the
same path.
:::

:::

:::step{type=concept title="One request's journey"}
The part of Spring that handles web requests is called **Spring MVC** (MVC stands for Model, View,
Controller, an old name from the days of server-rendered web pages; for REST APIs, think "Spring's web
layer"). The web starter set it all up for you in chapter 3.

Every request enters Spring through one front door, the **DispatcherServlet**, and it works like this telephone
operator: every call arrives at one board, and the operator plugs it through to the right line. One front door, and
a table of where everything goes.

:::photo{src="/lesson-images/spring/switchboard.webp" alt="A telephone operator at a manual switchboard in 1975, plugging cords into a panel of sockets" credit="Joseph A. Carr" license="Attribution" source="https://commons.wikimedia.org/wiki/File:Jersey_Telecom_switchboard_and_operator.jpg"}
A switchboard in 1975: one operator routes every call, like the DispatcherServlet routes every request.
:::

A request's journey is a sequence in time, so this picture plays. Press **▶ Play** and read each step:

:::diagram{name="request-journey"}
Only step 5 is your code. Spring does everything around it, the same way for every request.
:::

Three pieces from that journey are worth knowing by name, because they appear in logs and error
messages:

- **DispatcherServlet**: the single front door for all requests. ("Servlet" is the Java standard for code
  that handles web requests inside a server like Tomcat. Spring has exactly one, and it dispatches
  everything.)
- **Handler mapping**: the table from (method, path) to your Java method, built at start-up.
- **Message converter**: the piece that turns the request body into Java objects and your return value
  into JSON, using Jackson.

:::

:::step{type=example title="Spring's log, telling you the journey"}
Spring can narrate every request in its log. Start this chapter's project with web logging turned all the
way up (`TRACE` is the most detailed log level):

```bash run
cd 10-how-spring-handles-requests && mvn -q -o package -DskipTests && java -jar target/requests.jar --logging.level.org.springframework.web=TRACE
```

First look at the **start-up** part of the log. Among the lines, Spring lists every route it registered, per
controller. On our lab machine:

```text
c.s.c.CartController:
	{POST [/cart/items/{item}]}: add(String)
	{GET [/cart]}: cart()
o.s.b.a.w.s.e.BasicErrorController:
	{ [/error]}: error(HttpServletRequest)
	{ [/error], produces [text/html]}: errorHtml(HttpServletRequest,HttpServletResponse)
...
4 mappings in 'requestMappingHandlerMapping'
```

That is the handler mapping table, being built: 4 routes. (`c.s.c.CartController` is
`com.shop.cart.CartController`, shortened. `BasicErrorController` is Spring Boot's own controller that writes error
answers: JSON for programs, and the HTML Whitelabel page for browsers, chapter 3. More on it in chapter 17.)

Now send a request from a second terminal:

```bash run
curl localhost:8080/cart
```

and read what Terminal 1 printed for it. The first request also prints a few lines about the DispatcherServlet
getting ready (chapter 4); after those, on our lab machine, came these (class names shortened):

```text
DispatcherServlet : GET "/cart", parameters={}, headers={masked} in DispatcherServlet 'dispatcherServlet'
RequestMappingHandlerMapping : Mapped to com.shop.cart.CartController#cart()
HandlerMethod : Arguments: []
RequestResponseBodyMethodProcessor : Using 'application/json', given [*/*] and supported [application/json, application/*+json]
RequestResponseBodyMethodProcessor : Writing [[]]
RequestMappingHandlerAdapter : Applying default cacheSeconds=-1
DispatcherServlet : No view rendering, null ModelAndView returned.
DispatcherServlet : Completed 200 OK, headers={masked}
```

That is the journey from the animation, in Spring's own words: the request arrived at the DispatcherServlet, the
handler mapping found `CartController#cart()`, the method needed no arguments, the converter chose JSON (curl
accepts anything, `*/*`), wrote the empty list `[]`, and the request completed with 200. ("No view rendering" means
no HTML page was made; that is normal for a REST controller. `headers={masked}` hides the headers in the log, in
case they hold passwords.) Leave the app running for the next steps.
:::

:::step{type=concept title="404, 405, 406: three different no's"}
The journey also explains three error codes precisely, because each one comes from a different step:

- **404 Not Found** (step 3): no route matches the **path** at all.
- **405 Method Not Allowed** (step 3): the path exists, but not for that **method**. You saw this in
  chapter 1 with `PUT /menu/1`, and Spring even added an `Allow:` header listing the methods that do exist.
- **406 Not Acceptable** (step 6): your method ran fine, but the client asked for a format Spring cannot
  produce. Try it, asking for XML in the `Accept` header:

```bash run
curl -i -H "Accept: application/xml" localhost:8080/cart
```

```text
HTTP/1.1 406
Accept: application/json, application/*+json
Content-Length: 0
```

That is the real answer from our lab machine. The client said "I only accept XML"; Spring can only write JSON here
(only Jackson's JSON converter is present), so it refuses with an empty body, and its `Accept` header tells you what
it *can* produce. This step, choosing the format from the
`Accept` header, is called **content negotiation**. Browsers and curl send "anything is fine" by default,
so you rarely see 406, but now you know exactly what it means when you do.

Stop the app with Ctrl+C.
:::

:::step{type=predict title="Guess first"}
:::question
The app has only `@GetMapping("/cart")`. A client sends `DELETE /cart`. Which status comes back?
:::
- [ ] 404 Not Found
- [x] 405 Method Not Allowed
- [ ] 200 with an empty body
:::explain
The handler mapping knows the path `/cart`, but only for GET. A known path with an unknown method is
405, and the `Allow` header lists the methods that work.
:::
:::

:::step{type=concept title="A prefix for the whole class" file="10-how-spring-handles-requests/src/main/java/com/shop/cart/CartController.java" line="11-17"}
`CartController` is on the right. Its paths are `/cart` and `/cart/items/{item}`.

Real APIs usually put all their endpoints under a common prefix, very often with a **version**:
`/api/v1/cart`. Why the version? Because once phone apps are installed on millions of phones, you cannot
change the API they call. When you one day need a different shape of cart, you add `/api/v2/cart` next to
it, and old apps keep working on v1.

You could write the prefix on every method: `@GetMapping("/api/v1/cart")`,
`@PostMapping("/api/v1/cart/items/{item}")`... Repetitive, and one typo creates a route nobody calls.
Instead, put **`@RequestMapping`** on the **class**:

```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    @GetMapping            // GET /api/v1/orders
    public List<Order> all() { ... }

    @GetMapping("/{id}")   // GET /api/v1/orders/{id}
    public Order one(@PathVariable long id) { ... }
}
```

The class-level path is joined in front of every method's path. A method mapping with no path at all
(`@GetMapping` alone) means "the class path itself".

`@RequestMapping` is the general form behind all the others: `@GetMapping("/x")` is just short for
`@RequestMapping(method = GET, path = "/x")`. On a class, it is used without a method, as a shared prefix.
:::

:::step{type=task task=class_prefix title="Your turn: move the cart under /api/v1"}
Give `CartController` the prefix `/api/v1`, once, on the class, so its endpoints become
`GET /api/v1/cart` and `POST /api/v1/cart/items/{item}`. Do not change the method mappings.

The import is `org.springframework.web.bind.annotation.RequestMapping`. Rebuild and run, then:

```bash run
curl -X POST localhost:8080/api/v1/cart/items/kulfi; echo; curl -i localhost:8080/cart
```

The first adds kulfi and shows `["kulfi"]`. The second, the old path, is now 404. Press **Check**.

Usual slip: the prefix added to each method as well as to the class (then the path becomes
`/api/v1/api/v1/cart`).
:::

:::step{type=concept title="Same path, different methods" file="10-how-spring-handles-requests/src/main/java/com/shop/cart/CartController.java"}
The handler mapping matches on the **method and the path together**. That is what lets REST APIs reuse one
path for different actions on the same thing:

```java
@GetMapping("/cart")       // GET    /api/v1/cart  -> read the cart
public List<String> cart() { ... }

@DeleteMapping("/cart")    // DELETE /api/v1/cart  -> empty the cart
public List<String> empty() { ... }
```

Two Java methods, one path, no conflict: `GET /api/v1/cart` goes to `cart()` and `DELETE /api/v1/cart`
goes to `empty()`. This is the REST style from chapter 1, in code: the path names the thing (the cart), the
HTTP method says what to do with it.

What would be a conflict? Two methods with the same HTTP method **and** the same path. Spring refuses to
start, with an "Ambiguous mapping" error naming both methods. That is good: it catches the mistake
immediately.
:::

:::step{type=task task=method_routing title="Your turn: DELETE empties the cart"}
At the second TODO in `CartController`, add a method for **DELETE** on the cart's path (the same path as
the GET above it). It clears the cart's items and returns the list (now empty).

Rebuild, run, and try the whole conversation:

```bash run
curl -X POST localhost:8080/api/v1/cart/items/samosa; echo; curl -X DELETE localhost:8080/api/v1/cart; echo; curl localhost:8080/api/v1/cart
```

You should see `["samosa"]`, then `[]` twice. Press **Check**.

Usual slips: `@DeleteMapping("/api/v1/cart")` (the class already adds `/api/v1`, so write only `/cart`), or
returning a new empty list without clearing the field (the next GET then still shows the old items).
:::

:::step{type=concept title="One thread per request, and why it matters"}
Back to step 1 of the journey, because it has a consequence you met in chapter 9. Tomcat handles each request in
progress on its **own thread**, from a pool of at most 200 threads by default (the setting
`server.tomcat.threads.max`). So 50 customers loading their carts
at the same moment means 50 threads running *your* controller methods at the same moment.

But there is only **one** `CartController` object (a singleton). All 50 threads run the same object's
methods, sharing its fields. That is fine for code that only reads, and it is why controllers and
services should not keep per-customer data in fields.

Our chapter's cart breaks that rule on purpose, to keep the focus on routing: it keeps one list in a
field, so every client shares one cart. A real shop keeps each customer's cart in a database (Part 3), keyed
by the customer. Keep this in the back of your mind: **a controller field is shared by every request**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A class has `@RequestMapping("/api/v1/products")`, and a method has `@GetMapping("/{id}")`. Which request reaches the method?
:::
- [ ] GET /{id}
- [ ] GET /products/7
- [x] GET /api/v1/products/7
:::explain
The class path is joined in front of the method path: `/api/v1/products` + `/{id}`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which part of Spring decides which of your methods handles a request?
:::
- [ ] Tomcat
- [x] The handler mapping, consulted by the DispatcherServlet
- [ ] Jackson
:::explain
Tomcat only delivers the request to the DispatcherServlet; the handler mapping looks up (method, path) in
the table built at start-up. Jackson converts JSON.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Your method ran, but the client gets 406. What is wrong?
:::
- [ ] The path is not mapped
- [ ] The method threw an exception
- [x] The client's Accept header asks for a format Spring cannot write
:::explain
406 comes from content negotiation, after your method has run: the client wants (say) XML, and only JSON
can be produced.
:::
:::

:::step{type=deep-dive title="Go deeper: filters, interceptors, and MVC vs WebFlux"}
**Around the journey.** Two kinds of hooks sit around this journey. **Filters** run before the
DispatcherServlet even sees the request (security checks, request ids); **interceptors** run just before
and after your method. Chapter 18 builds both.

**Spring MVC vs WebFlux.** Spring also has a second web stack, **WebFlux**, which does not use one thread
per request; instead a few threads juggle many requests with non-blocking code. It is useful for very high
numbers of slow connections, but harder to write and debug. Most Spring Boot services use MVC, the
one-thread-per-request model you learned here, and since Java 21, **virtual threads**
(`spring.threads.virtual.enabled=true`) let MVC handle huge numbers of waiting requests too, with the same
simple code.
:::

:::step{type=recap title="What you can do now"}
You can now follow any request through Spring:

- Tomcat gives each request a thread; the **DispatcherServlet** receives every request; the **handler
  mapping** finds your method by HTTP method and path; Spring prepares the arguments; your method runs; a
  **message converter** (Jackson) writes the result as JSON.
- **404**: no route for the path. **405**: the path exists, not for that method. **406**: the client wants a
  format Spring cannot write (**content negotiation**).
- `--logging.level.org.springframework.web=TRACE` makes Spring narrate the routes at start-up and every
  request.
- **`@RequestMapping` on the class** gives every endpoint a shared prefix, such as `/api/v1`.
- The same path can have different Java methods for different HTTP methods.
- One controller object serves every request at once: no per-customer data in fields.

:::photo{src="/lesson-images/spring/spring-10-notes.webp" alt="Sketchnote: How Spring handles a request. Every request goes through the DispatcherServlet, the one front door. Flow: Tomcat thread, DispatcherServlet, handler mapping, your method, Jackson writes JSON. Remember: 404 no route for the path; 405 the path exists but not that method; 406 the client wants a format Spring cannot write; @RequestMapping on the class adds a prefix." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 11: reading everything a request carries, from path variables to query parameters and headers.
:::
