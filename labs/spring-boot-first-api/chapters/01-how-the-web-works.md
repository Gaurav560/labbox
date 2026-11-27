:::step{type=story title="Before we write a server"}
In chapter 0 you started a server and it answered "404". To build a good backend, you need to speak its
language fluently: **HTTP**. Every Spring annotation you will learn later (`@GetMapping`, `@PostMapping`,
`@PathVariable`, `ResponseEntity`...) is just a Java way of saying something in HTTP. If HTTP is clear in
your head, Spring will feel natural. If it is fuzzy, Spring will feel like magic words.

So this chapter has no Spring code to write. Instead, there is a small finished **API** already in your project.
An API (Application Programming Interface) is a set of addresses a program offers so that other programs can use
it; ours is a **canteen menu**. You will start it and talk to it directly, the way a phone app or a browser would,
using `curl`. You will read real requests and real responses, and by the end you will be able to read any HTTP
conversation and say exactly what happened.

:::mission
Start the menu API, explore it with curl, and write down what it really answered in `answers.properties`.
:::
:::

:::step{type=concept title="A conversation in two halves"}
Every interaction on the web is a short conversation between two programs:

- The **client** asks. A browser, a phone app, another server, or `curl` in your terminal.
- The **server** answers. That is what we are learning to build.

The client always speaks first. It sends a **request**. The server reads it, does some work, and sends back
exactly one **response**. Then that conversation is over. The next request is a brand new conversation: HTTP
itself does not remember the previous one. This is called being **stateless**. When an app does need to remember
you (a login, a shopping cart), the client sends a small reminder with every request, such as a cookie, a
token or the login details themselves; chapter 28 shows a login travelling with each request. Statelessness is a big reason the web scales well: if the server keeps no memory
between requests, any of many identical copies of it can answer any request.

It all began on one machine. In 1990 at CERN, Tim Berners-Lee wrote the first web server and the first browser on
this NeXT computer. The label on it says it all: "This machine is a server. DO NOT POWER IT DOWN!!"

:::photo{src="/lesson-images/spring/first-web-server.webp" alt="The NeXT computer at CERN that ran the first web server, with a handwritten label on the case saying This machine is a server, DO NOT POWER IT DOWN, next to its keyboard and Tim Berners-Lee's proposal" credit="Coolcaesar at English Wikipedia" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:First_Web_Server.jpg"}
The first web server, at CERN. Every Spring Boot app you build is its great-grandchild.
:::

Both the request and the response are just **text**, in a fixed format. That is the nice thing about
HTTP: you can read it with your own eyes. Let's look at one.

:::

:::step{type=concept title="What a request looks like"}
Here is a complete HTTP request, exactly as it travels over the network:

```text
GET /menu/2 HTTP/1.1
Host: localhost:8080
Accept: application/json
```

Line by line:

**`GET /menu/2 HTTP/1.1`** is the **request line**, the most important line. It has three parts:
- `GET` is the **method**: *what* the client wants to do. GET means "give me".
- `/menu/2` is the **path**: *which thing* it wants. Here, menu item number 2.
- `HTTP/1.1` is the version of HTTP being spoken. You can mostly ignore it.

**`Host: localhost:8080`** and **`Accept: application/json`** are **headers**: extra information, one per line,
written as `Name: value`. `Host` says which server the request is for. `Accept` says "I would like the answer in
JSON, please"; `application/json` is the official name for JSON content (such names are called media types).

A request can also carry a **body**: data the client sends, like the details of a new menu item. A GET
request has no body. We will see one with a body soon.
:::

:::step{type=concept title="The parts of a URL"}
When you type an address in a browser, or give one to curl, you are writing a **URL**. Here is one with
every part labelled:

```text
http://localhost:8080/menu/search?maxPrice=2000&sort=name
\__/   \_______/ \__/\__________/ \______________________/
scheme   host    port    path            query string
```

- **scheme** `http`: the protocol. On the real internet it is usually `https`, the encrypted version.
- **host** `localhost`: which computer. `localhost` is a special name that always means *this very
  machine*. Your server and your curl run on the same lab machine, so that is where we connect.
- **port** `8080`: which program on that computer. One machine can run many servers, each listening on
  its own numbered port. Spring Boot uses 8080 unless you tell it otherwise.
- **path** `/menu/search`: which **resource** on that server. A resource is any thing the server can hand out or
  change: the whole menu, one item, an order.
- **query string** `?maxPrice=2000&sort=name`: optional extra parameters, after a `?`, as `name=value` pairs joined
  with `&`. Usually used for searching, filtering and sorting.

This URL is an example to show the parts. Our canteen API has no search, so if you try it you get a `400` (a
status code explained in a moment). In this lab you will mostly write things like `localhost:8080/menu`: curl
fills in `http://` for you, and the path `/` is the default when you leave the path out.
:::

:::step{type=concept title="What a response looks like"}
And here is the server's answer to `GET /menu/2`:

```text
HTTP/1.1 200
Content-Type: application/json

{"id":2,"name":"Samosa","pricePaise":1800}
```

(`pricePaise` is the price in paise, the smallest unit of the rupee: 1800 paise is Rs 18. Money is kept in whole
paise so that no decimals can round wrongly; chapter 12 comes back to this.)

The first line is the **status line**. Its key part is the **status code**, a three-digit number that
says how it went. `200` means "OK, here is what you asked for".

(You may have seen `200 OK` written with the words. Those words are optional, and Tomcat, the server
inside Spring Boot, leaves them out. Only the number matters to programs.)

Then come **headers**, the same `Name: value` format as in the request. `Content-Type:
application/json` tells the client "the body below is JSON, read it as JSON".

Then **one empty line**, and then the **body**: the actual data. The empty line is how HTTP knows where
the headers end and the body begins.

:::diagram{name="http-conversation"}
A request for one menu item, and the response our lab machine really sent back, part by part.
:::
:::

:::step{type=concept title="Status codes: the five families"}
You do not need to memorise all the status codes. You need to know the five families, which you can tell
by the first digit, and a handful of common codes.

- **1xx**: "wait, more is coming". Rare; you will almost never see these.
- **2xx Success.** It worked.
  - `200 OK`: here is the result.
  - `201 Created`: I made the new thing you sent me.
  - `204 No Content`: done, and there is nothing to send back (for example after a delete).
- **3xx Redirection.** Look somewhere else. `301` / `302`: the thing has moved to another address.
- **4xx Client error.** *You* (the client) asked for something wrong.
  - `400 Bad Request`: what you sent does not make sense (missing fields, bad JSON).
  - `401 Unauthorized`: who are you? Log in first. (The name is old and misleading: it really means "not logged
    in".)
  - `403 Forbidden`: I know who you are, but you are not allowed to do this.
  - `404 Not Found`: there is nothing at that address.
  - `405 Method Not Allowed`: that address exists, but not for that method.
  - `409 Conflict`: that clashes with what already exists (a duplicate, for example).
- **5xx Server error.** *The server* broke. `500 Internal Server Error`: a bug or crash on the server side.
  `503 Service Unavailable`: the server is overloaded or something it depends on is down.

The difference between 4xx and 5xx matters a lot: **4xx means the client should change its request;
5xx means the server team has a problem to fix.** A good backend never answers 500 for a mistake the
client made.
:::

:::step{type=concept title="Methods: what the client wants to do"}
The method is the verb of the request. There are a few, and each has a clear meaning:

- **GET**: read something. Never changes anything on the server. Safe to repeat as often as you like.
- **POST**: create something new (or trigger an action). Sending the same POST twice usually creates two things.
- **PUT**: replace something completely with what I send.
- **PATCH**: change part of something (just the price, say).
- **DELETE**: remove something.

Notice the pattern: the **path names a thing** (a noun, like `/menu` or `/menu/2`), and the **method says what
to do with it** (a verb). So you do not write `/getMenu` or `/deleteItem?id=2`. You write `GET /menu` and
`DELETE /menu/2`. APIs designed this way are called **REST** APIs (REST stands for Representational State
Transfer, a name from Roy Fielding's 2000 doctoral thesis; chapter 10 tells that story). Most web APIs today,
including the one you will build, follow this style.

Here is our menu API in that style:

```text
GET    /menu       -> the whole menu
GET    /menu/2     -> one item
POST   /menu       -> add an item (the item is in the body)
DELETE /menu/2     -> remove an item
```
:::

:::step{type=concept title="JSON, the language of the data"}
The body of most API requests and responses is **JSON** (JavaScript Object Notation). Despite the name,
every language uses it. It has only a few building blocks:

```json
{
  "id": 2,
  "name": "Samosa",
  "pricePaise": 1800,
  "vegetarian": true,
  "tags": ["snack", "fried"],
  "discount": null
}
```

- `{ ... }` is an **object**: a set of `"name": value` pairs, separated by commas. Names are always in
  double quotes.
- Values can be **strings** (`"Samosa"`, always double quotes), **numbers** (`1800`, no quotes),
  **booleans** (`true` / `false`), `null` (nothing), another object, or an **array**.
- `[ ... ]` is an **array**: a list of values in order.

A Java object maps to JSON very naturally: each field becomes a `"name": value` pair, and a Java `List`
becomes an array. Spring does this conversion for you automatically, in both directions. That is why,
in the next chapters, you will return plain Java objects from your methods and they arrive at the
client as JSON.

One common beginner mistake: single quotes. `{'name': 'Samosa'}` is **not** valid JSON. Always double.
:::

:::step{type=try title="Start the menu API" file="01-how-the-web-works/src/main/java/com/shop/MenuController.java"}
Enough reading; let's talk to a server. The menu API's code has opened on the right. You do not need to
understand it yet (you will write code exactly like this in the coming chapters). Just glance at the
`@GetMapping`, `@PostMapping` and `@DeleteMapping` lines: each one connects a method and a path to a
piece of Java.

Start the server in your terminal:

```bash run
cd 01-how-the-web-works && mvn -q -o package -DskipTests && java -jar target/menu-api.jar
```

Wait for the line that starts with `Started ShopApiApplication` (on our lab machine it came after about 1.2
seconds). The server is now running and waiting. Leave it running.

Now open a **second terminal** with the **+** next to the Terminal tab. That is where you will be the
client. (Your server stays busy in Terminal 1; Terminal 2 is free for typing requests.)
:::

:::step{type=example title="Your first request with curl"}
In Terminal 2, ask the server for the whole menu:

```bash run
curl -i localhost:8080/menu
```

`curl` sends a GET request to that URL. The `-i` option means "also **include** the status line and
headers in what you show me". Without `-i`, curl prints only the body. You will see:

```text
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Sat, 21 Nov 2026 11:25:13 GMT

[{"id":1,"name":"Mango kulfi","pricePaise":2000},{"id":2,"name":"Samosa","pricePaise":1800},{"id":3,"name":"Fruit custard","pricePaise":3000}]
```

Read it the way you learned: status `200`, so it worked. `Content-Type: application/json`, so the body is JSON.
`Transfer-Encoding: chunked` means the server sends the body in pieces without saying its total length first, and
`Date` is when the server answered; you can ignore both. Then the empty line, then the body: a JSON **array** of
three **objects**, one per menu item.

Now try one item, and one that does not exist:

```bash run
curl -i localhost:8080/menu/2
```

```bash run
curl -i localhost:8080/menu/42
```

The first answers `200` with a single object. The second answers `404` with `Content-Length: 0`: the body is
empty, zero bytes long. The server is fine; there just is no item 42. Look carefully at each answer: you will need
these values for your task.
:::

:::step{type=task task=http_status title="Your turn: write down what the server said"}
The file `01-how-the-web-works/answers.properties` has opened on the right. Using the answers you just
got (run the commands again if you need to), fill in the three values under the first TODO:

- the status code of `GET /menu`,
- the status code of `GET /menu/42`,
- the `Content-Type` of `GET /menu`.

Write only the value after the `=`, with no quotes and no spaces, then press **Check**.

Usual slips: writing `200 OK` instead of just the number, or copying a whole header line (`Content-Type:
application/json`) instead of only its value (`application/json`).
:::

:::step{type=example title="Sending data: a POST with a body"}
Reading is half of an API. Now let's add something to the menu. To create, we use **POST**, and the new
item travels in the request **body**, as JSON:

```bash run
curl -i -X POST localhost:8080/menu -H "Content-Type: application/json" -d '{"name": "Vada pav", "pricePaise": 2500}'
```

That command is longer, so let's take it apart:

- `-X POST` sets the method. (Without it, curl sends GET.)
- `-H "Content-Type: application/json"` adds a **header** telling the server: "the body I am sending is JSON".
- `-d '...'` is the **data**, the request body. Notice the JSON is inside **single quotes**: those are for
  your shell, so the double quotes inside reach the server untouched.

The server answers:

```text
HTTP/1.1 201
Location: /menu/4
Content-Type: application/json

{"id":4,"name":"Vada pav","pricePaise":2500}
```

`201 Created`, not 200: the server is being precise, saying "I created something". The `Location` header says
*where* the new item now lives. And the body is the new item, with the `id` the server chose for it (this API
takes the highest id so far and adds one: 3 + 1 = 4). Check that it is really there:

```bash run
curl localhost:8080/menu/4
```
:::

:::step{type=example title="Removing data, and using the wrong method"}
Now remove the samosa:

```bash run
curl -i -X DELETE localhost:8080/menu/2
```

The answer is `204` with no body at all: "done, nothing to send back". Ask for it again and you will get
`404`, because it is gone:

```bash run
curl -i localhost:8080/menu/2
```

Finally, try a method this API does not support for that path. Our API has no PUT:

```bash run
curl -i -X PUT localhost:8080/menu/1
```

You get `405 Method Not Allowed`. On our lab machine the answer was:

```text
HTTP/1.1 405
Allow: DELETE, GET
Content-Type: application/json
...
{"timestamp":"2026-11-27T20:27:45.298+00:00","status":405,"error":"Method Not Allowed","path":"/menu/1"}
```

Look at the `Allow` header: the server even tells you which methods *are* allowed at that path, here DELETE and
GET. Spring added that for free, because it knows every path and method you mapped.

When you are done, go back to **Terminal 1** and stop the server with **Ctrl+C**.
:::

:::step{type=task task=http_methods title="Your turn: the answers that changed the menu"}
In the same `answers.properties`, fill in the values under the second TODO:

- the status code of your `POST /menu`,
- the `Location` header it returned,
- the status code of `DELETE /menu/2`.

Press **Check** when you are done.

Usual slips: if you sent the POST twice, the second item got `/menu/5`; the check expects the answer to the
*first* POST on a fresh menu, `/menu/4`. Restarting the server resets the menu to its three items, and a new POST
then gets `/menu/4` again.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A client sends a POST with broken JSON in the body (a missing quote). Which status code fits best?
:::
- [ ] 500 Internal Server Error
- [x] 400 Bad Request
- [ ] 404 Not Found
:::explain
The *client* sent something wrong, so it is a 4xx, and "this does not make sense" is 400. A 500 would
blame the server for the client's mistake.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which request is designed in the REST style?
:::
- [ ] GET /deleteProduct?id=7
- [x] DELETE /products/7
- [ ] POST /products/7/delete
:::explain
The path names the thing (`/products/7`) and the method says what to do with it (`DELETE`). The others
hide the action in the path.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which of these is valid JSON?
:::
- [ ] {'name': 'Kulfi', 'price': 20}
- [ ] {name: "Kulfi", price: 20}
- [x] {"name": "Kulfi", "price": 20}
:::explain
JSON needs double quotes around names and string values. Single quotes, or names without quotes, are
fine in JavaScript code but not in JSON.
:::
:::

:::step{type=deep-dive title="Go deeper: HTTPS, HTTP/2 and idempotency"}
**HTTPS** is HTTP inside an encrypted connection (TLS, Transport Layer Security). The requests and responses look
exactly the same, but nobody in between can read or change them. In production, a Spring Boot app often speaks
plain HTTP inside the company's network, and a **load balancer** or **proxy** in front of it (a server that
receives the internet's requests and passes them on to your app) handles HTTPS.

**HTTP/2 and HTTP/3** send the same requests in a faster, binary way (many requests over one connection).
The methods, paths, headers and status codes you learned here are identical.

**Idempotent** is a word you will meet: a request is idempotent when sending it twice has the same effect
as sending it once. GET, PUT and DELETE are idempotent (deleting an item twice leaves it deleted); POST is
not (posting twice creates two items). This is why clients may safely retry a failed GET, but must be
careful retrying a POST, for example when paying.
:::

:::step{type=recap title="What you can do now"}
You can now read any HTTP conversation:

- A **request** has a method, a path, headers, and sometimes a body. A **response** has a status code,
  headers, and usually a body.
- A **URL** is scheme, host, port, path and query string.
- **Status codes**: 2xx worked, 4xx the client got it wrong, 5xx the server broke. You know 200, 201,
  204, 400, 401, 403, 404, 405, 409, 500 and 503.
- **Methods**: GET reads, POST creates, PUT replaces, PATCH changes part, DELETE removes. In **REST**, the
  path is a noun and the method is the verb.
- **JSON**: objects, arrays, strings in double quotes, numbers, booleans and null.
- With **curl** you can play the client: `-i` to see headers, `-X` for the method, `-H` for a header, `-d` for a
  body.

:::photo{src="/lesson-images/spring/spring-01-notes.webp" alt="Sketchnote: How the web works. A client sends a request and the server sends one response. Flow: method and path, headers, body, status code. Remember: 2xx worked, 4xx the client's mistake, 5xx the server broke; GET reads, POST creates, DELETE removes; curl -i shows the headers." ai="true"}
One page of notes for this chapter.
:::

Everything from here on is about writing the server side of these conversations in Spring. First, chapter
2 looks at the project itself: Maven and the pom.xml.
:::
