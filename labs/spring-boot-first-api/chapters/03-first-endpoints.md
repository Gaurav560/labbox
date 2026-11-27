:::step{type=story title="Your first lines of Spring"}
In chapter 1 you were the client: you sent requests with curl and read the answers. In chapter 0 your own
server answered every request with 404, because nothing in it handled any address.

Today that changes. You will write the server side of an HTTP conversation: a method in your code that Spring calls
when a request arrives, and whose return value becomes the response. A method together with the address it
answers (a method and a path, like `GET /hello`) is called an **endpoint**. Once you have written one, you have
the pattern for hundreds.

We will build the Shop API's first two endpoints: a greeting, and a list of the shops (merchants) that
sell on our platform, as JSON.

:::mission
Add `GET /hello` and `GET /merchants` to the Shop API, and see both answer in curl and in the Preview tab.
:::
:::

:::step{type=concept title="Where requests go: controllers"}
When a request arrives, Spring needs to know **which of your methods** should handle it. You tell it with
two things:

1. A class marked as a **controller**: "this class contains methods that handle web requests".
2. On each method, a **mapping**: "this method handles *this method* (GET, POST...) on *this path*".

A controller is just a normal Java class. Spring finds it at start-up (because of its annotation), creates one
object of it, and from then on every matching request is routed to one of its methods. ("Routed" means sent to the
right place, like a letter sorted to the right house.) You
never create the controller and you never call its methods. Spring does both. (Remember inversion of
control from chapter 0? This is it, in practice.)

Here is the smallest possible controller, with one endpoint:

```java
@RestController
public class StatusController {

    @GetMapping("/status")
    public String status() {
        return "ok";
    }
}
```

That is a complete, working endpoint. Let's read it piece by piece in the next step.
:::

:::step{type=concept title="Reading it line by line"}
```java
@RestController
public class StatusController {
```

**`@RestController`** marks the class as a controller for a REST API. It tells Spring two things: create
this class at start-up and route requests to it; and *whatever its methods return is the response body*.
(There is also a plain `@Controller`, used for web pages built on the server. For APIs, you always want
`@RestController`.)

```java
    @GetMapping("/status")
```

**`@GetMapping("/status")`** connects this method to **GET requests for the path `/status`**. There is one of these
for each common HTTP method: `@GetMapping`, `@PostMapping`, `@PutMapping`, `@PatchMapping`, `@DeleteMapping`.
Write the path starting with `/`, as all Spring code does. (If you forget the slash, Spring adds it: on our lab
machine `@GetMapping("status")` still answered `/status`. But the slash makes the path clear to every reader.)

```java
    public String status() {
        return "ok";
    }
```

A normal Java method. Its **name does not matter** to Spring (call it anything clear); the mapping is what connects
it to the URL. Whatever it **returns** is sent back to the client as the response body, with status `200`. A
`String` is sent as plain text: on our lab machine the answer had `Content-Type: text/plain;charset=UTF-8`
(UTF-8 is the usual way of writing text as bytes) and the body was exactly `ok`.

So the whole conversation looks like this:

```text
GET /status            ->  Spring finds status()  ->  it returns "ok"  ->  HTTP/1.1 200   body: ok
```
:::

:::step{type=example title="Returning objects: JSON for free"}
Returning text is nice, but APIs mostly return **data**. Here is the part that feels like magic the first
time: if your method returns a Java object or a list, **Spring turns it into JSON for you**.

The format itself was named and written down in 2001 and 2002 by **Douglas Crockford**, an American programmer who
noticed that JavaScript's way of writing objects made a good way to send data between any two programs.

:::photo{src="/lesson-images/spring/crockford.webp" alt="Douglas Crockford, a smiling man with grey hair, a beard and glasses, in a dark jacket" credit="Robert Claypool" license="CC0" source="https://commons.wikimedia.org/wiki/File:Douglas_Crockford,_February_2013.jpg"}
Douglas Crockford, who wrote down the JSON format that Spring produces for you in this step.
:::

```java
public record Product(long id, String name, int pricePaise) { }

@RestController
public class ProductController {

    @GetMapping("/products/featured")
    public Product featured() {
        return new Product(1, "Mango kulfi", 2000);
    }

    @GetMapping("/products/names")
    public List<String> names() {
        return List.of("Mango kulfi", "Samosa");
    }
}
```

(A **record** is a short way to write a Java class that just holds data. The fields go in the brackets, and Java
writes the constructor and a method to read each field for you, named after the field: `id()`, `name()`,
`pricePaise()`. You will use records a lot.)

The responses (we ran this example on our lab machine):

```text
GET /products/featured  ->  {"id":1,"name":"Mango kulfi","pricePaise":2000}
GET /products/names     ->  ["Mango kulfi","Samosa"]
```

Each field of the record became a `"name": value` pair of a JSON **object**. The `List` became a JSON
**array**. And Spring set the header `Content-Type: application/json`, so the client knows what it is
reading.

Who did the conversion? **Jackson**, the JSON library the web starter brought in (you saw it in the
dependency tree in chapter 2). Spring hands your return value to Jackson, and Jackson writes the JSON.
You will customise this later; for now, enjoy that it just works.

:::

:::step{type=predict title="Guess first"}
:::question
A controller method returns `List.of(3, 1, 2)`. What does the client receive?
:::
- [ ] The text 3, 1, 2
- [x] The JSON array [3,1,2]
- [ ] The JSON array [1,2,3], sorted
:::explain
A list becomes a JSON array, in the same order as the list. Spring never sorts anything for you: if you
want sorted output, you sort it in your method. (Remember that for the second task.)
:::
:::

:::step{type=concept title="The Shop API's controller" file="03-first-endpoints/src/main/java/com/shop/MerchantController.java" line="8-16"}
Now open your own project: `MerchantController.java` is on the right.

It is a `@RestController` already, so Spring creates it and is ready to route requests to it. It has a
list of the merchants who sell on our platform:

```java
static final List<String> MERCHANTS = List.of("Kirana King", "Book Point", "Annapurna Mess");
```

(`static final` means it belongs to the class and never changes: a constant. `List.of` makes a list that
cannot be modified.)

And then two TODO comments, one for each task. But no methods. Which means that right now, every request
to this app gets... you know the answer by now: 404.
:::

:::step{type=try title="Build and run" file="03-first-endpoints/src/main/java/com/shop/MerchantController.java" line="13"}
Let's see that 404 with our own eyes before fixing it. Build and start the app:

```bash run
cd 03-first-endpoints && mvn -q -o package -DskipTests && java -jar target/shop-api.jar
```

Open a second terminal with **+**, and ask for the greeting:

```bash run
curl -i localhost:8080/hello
```

`404`, with a JSON error body like the one you saw in chapter 0. Now stop the server (Ctrl+C in Terminal 1).

One thing to know before you change code: **the running app does not see your edits**. Java compiled your
code when you built the jar. Every time you change a `.java` file, you build and start the app again. It
will become a habit: change, Ctrl+C, build and run, try.
:::

:::step{type=task task=hello title="Your turn: GET /hello"}
In `MerchantController.java`, at the first TODO, add a method that handles **GET** requests for **`/hello`**
and returns the text `Hello from the Shop API!` (exactly that: capital H, capital S, capital A, and the
exclamation mark).

The steps:

1. Above a new method, write `@GetMapping("/hello")`.
2. Write a `public` method that returns a `String` (name it `hello`, for example).
3. In it, return the greeting text.

Use the `StatusController` example from earlier as your pattern. Then rebuild, run, and try:

```bash run
curl -i localhost:8080/hello
```

You should get `200`, `Content-Type: text/plain;charset=UTF-8` and your greeting. Press **Check**.

Usual slips: the greeting text not exactly the same (a missing `!`, a lower-case letter), the method placed
outside the class's `{ }`, or a missing import for `GetMapping` (the editor offers to add it).
:::

:::step{type=try title="See it in the Preview tab"}
curl is not the only client. Your lab has a small built-in browser: the **Preview** tab next to the
Terminal. With the app running, click **Preview**. It opens `localhost:8080/hello` from your lab machine,
and shows your greeting.

You can type another path in its address box, like `/merchants`. It is not written yet, so you will see Spring's
**Whitelabel Error Page**: the 404 page Spring shows to browsers. Spring sends a small HTML page instead of JSON
because a browser's request says it prefers HTML (in its `Accept` header).

This is what a real browser does: send a GET request and display the body. Typing an address in a browser always
sends a GET; sending POST, PUT or DELETE needs a form or some JavaScript. That is why curl stays our main tool for
testing APIs.
:::

:::step{type=example title="Working with the list before returning it"}
Your second endpoint returns the merchants, but **sorted A to Z**. The list in `MERCHANTS` is not sorted,
and it is a constant you should not change. So the method has to make a **sorted copy** and return that.

Java gives you a neat way to do that with a **stream**: take the items one by one, put them through some
steps, and collect the result. Here is the same idea on a list of numbers, sorted largest first:

```java
List<Integer> scores = List.of(40, 95, 70);

List<Integer> ranked = scores.stream()                       // take the items one by one
        .sorted(Comparator.reverseOrder())                   // sort them, largest first
        .toList();                                           // collect them into a new list

// ranked is [95, 70, 40]; scores is unchanged: [40, 95, 70]
```

`.sorted()` with nothing in the brackets sorts in **natural order**: numbers smallest first, and `String`s
alphabetically, A to Z. That is exactly what you need. And the original list is never touched: the stream
builds a brand new one.

Here is where your next method fits, traced on our lab machine once it was written:

:::diagram{name="first-endpoint"}
GET /merchants on our lab machine, from the request to the JSON answer.
:::
:::

:::step{type=task task=merchants title="Your turn: GET /merchants, A to Z"}
At the second TODO, add a method for **GET `/merchants`** that returns the merchant names **sorted A to Z**,
as a `List<String>`.

The steps: a `@GetMapping("/merchants")` method that returns `List<String>`; inside it, `MERCHANTS.stream()`,
then `.sorted()`, then `.toList()`.

Rebuild, run, and try it:

```bash run
curl -i localhost:8080/merchants
```

You should see `Content-Type: application/json` and the array
`["Annapurna Mess","Book Point","Kirana King"]`. Spring and Jackson turned your list into JSON. Press **Check**.

Usual slips: returning `MERCHANTS` itself (then the order is the list's own order, not A to Z), or trying to sort
`MERCHANTS` in place with `Collections.sort` (a list made with `List.of` cannot be changed, so that throws an
error).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
You add a method with `@GetMapping("/hello")`, but forget `@RestController` on the class. What does GET /hello return?
:::
- [ ] Your greeting, as normal
- [x] 404: without the annotation, Spring never creates the class, so nothing handles /hello
- [ ] 500: Spring crashes
:::explain
Spring only routes to classes it knows about. Without `@RestController`, the class is just a normal Java
class that nobody creates, and its mappings are never registered.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
You rename the method `hello()` to `sayHi()`, keeping `@GetMapping("/hello")`. Does `GET /hello` still work?
:::
- [x] Yes: the mapping decides the URL, not the method name
- [ ] No: the method must be called hello
- [ ] Only after you also rename the class
:::explain
Spring connects URLs to methods through the mapping annotation. Method names are for humans: choose clear ones.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
You changed the greeting text, saved, and curl still shows the old text. Why?
:::
- [ ] Spring caches responses
- [x] The app running is the old build; stop it, build and run again
- [ ] curl caches responses
:::explain
The running jar was built from your old code. Every code change needs a rebuild and a restart. (Chapter 27
mentions DevTools, which can restart automatically.)
:::
:::

:::step{type=deep-dive title="Go deeper: @ResponseBody, and other return types"}
`@RestController` is really two annotations in one: `@Controller` (a class that handles requests) plus
`@ResponseBody` (write the return value into the response body). With a plain `@Controller`, Spring would
treat a returned `String` as the *name of an HTML page template* to render instead. That is how classic
server-rendered websites work, with templates like Thymeleaf. For JSON APIs, `@RestController` is what you
want.

Return types you will meet: `String` (plain text), any object or record (a JSON object), `List` and
arrays (a JSON array), `Map` (a JSON object built from keys), and `ResponseEntity<T>`, which lets you
choose the status code and headers too. Chapter 13 is all about `ResponseEntity`.
:::

:::step{type=recap title="What you can do now"}
You wrote your first two endpoints. You now know:

- A **controller** is a class marked `@RestController`. Spring creates it and routes requests to it.
- `@GetMapping("/path")` (and `@PostMapping`, `@PutMapping`, `@PatchMapping`, `@DeleteMapping`) connects a
  method and a path to one of your methods. The method's name does not matter.
- The method's **return value is the response body**: a `String` is sent as plain text; objects, records
  and lists are turned into **JSON** by **Jackson**, with `Content-Type: application/json`.
- A **record** is a short way to write a data class.
- After changing code: stop, build and run again.
- You can test with curl, and see GET responses in the **Preview** tab.

:::photo{src="/lesson-images/spring/spring-03-notes.webp" alt="Sketchnote: First endpoints. A controller method plus a mapping becomes an endpoint. Flow: GET /hello arrives, Spring finds the mapping, your method runs, its return value is the body. Remember: @RestController on the class; a String goes out as plain text; records and lists go out as JSON; after a change, rebuild and restart." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4 slows down and follows exactly what happens when the app starts: how Spring found your
controller in the first place.
:::
