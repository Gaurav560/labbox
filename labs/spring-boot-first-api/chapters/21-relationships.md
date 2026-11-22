:::step{type=story title="Things that belong together"}
An order is not just a row on its own. Asha's order contains two lines: two mango lassis and three samosas.
In the database, those lines live in their own table, `order_item`, and each one points back to its order. In
Java, you would like to write `order.getItems()` and get the list. Making those two worlds meet is what JPA
**relationships** are for.

Relationships are also where JPA has its most famous trap. A completely innocent-looking line of Java can make
your app run **hundreds of queries** for one page, and it works perfectly in development, then crawls in
production. It is called the **N+1 problem**, every Spring developer meets it, and in this chapter you will
see it happen in the SQL log, then fix it.

:::mission
Map orders and their items as a JPA relationship, then load the order list in one query instead of six.
:::
:::

:::step{type=concept title="How databases link rows: foreign keys"}
In a relational database, an order and its items are two tables. Each item row stores **the id of its order**
in a column, here `order_id`:

:::diagram{name="one-to-many"}
The order_id column in order_item points back to a row in orders.
:::

```text
orders                         order_item
+----+----------+              +----+---------------+----------+-------------+----------+
| id | customer |              | id | product       | quantity | price_paise | order_id |
+----+----------+              +----+---------------+----------+-------------+----------+
|  1 | Asha     |  <---------  |  1 | Mango lassi    |        2 |        2000 |        1 |
|  2 | Ravi     |  <----+----  |  2 | Samosa        |        3 |        1800 |        1 |
+----+----------+       +----  |  3 | Filter coffee |        1 |        3000 |        2 |
                               +----+---------------+----------+-------------+----------+
```

A column that holds another table's primary key is a **foreign key**. The link always lives on the "many"
side: many items point to one order. An order row knows nothing about its items; you find them by asking
"which items have `order_id = 1`?".

This is called a **one-to-many** relationship (one order, many items), or seen from the other side,
**many-to-one** (many items, one order).
:::

:::step{type=concept title="Mapping it: @ManyToOne and @OneToMany"}
JPA maps that foreign key to plain Java references, on both sides. Here it is for a different pair: a blog
`Post` with many `Comment`s.

**The many side** (the one with the foreign key column):

```java
@Entity
public class Comment {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String text;

    @ManyToOne                                // many comments, one post
    @JoinColumn(name = "post_id")             // the foreign key column
    private Post post;
}
```

**The one side** (optional, but handy: it gives you `post.getComments()`):

```java
@Entity
public class Post {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL)
    private List<Comment> comments = new ArrayList<>();
}
```

Three details to read slowly:

- **`@JoinColumn(name = "post_id")`** names the foreign key column. The `Comment` side **owns** the
  relationship: it is the side whose table has the column.
- **`mappedBy = "post"`** on the other side says: "I am not a separate link; I am the same relationship,
  already mapped by the field called `post` in `Comment`". Without it, JPA would think these are two
  different relationships and invent an extra table.
- **`cascade = CascadeType.ALL`** means: whatever you do to the post (save, delete), do it to its comments
  too. Save a new post with three comments, and all four rows are inserted.
:::

:::step{type=try title="The project, unmapped" file="21-relationships/src/main/java/com/shop/order/OrderItem.java" line="21-23"}
This chapter's project has `CustomerOrder` (in a table called `orders`, because `order` is a reserved word in
SQL) and `OrderItem`. Look at `OrderItem.java` on the right: the `order` field is a plain field, with no
mapping. Run the app:

```bash run
cd 21-relationships && mvn -q -o package -DskipTests && java -jar target/relationships.jar
```

It fails at start-up. Among the error lines:

```text
Caused by: org.hibernate.MappingException: Basic collection has element type 'com.shop.order.OrderItem' which is not a known basic type
```

Hibernate looked at `CustomerOrder.items`, a list of `OrderItem`s, and tried to store it like a plain value in
a column, which is impossible. The same goes for `OrderItem.order`: a whole `CustomerOrder` cannot fit in one
column of `order_item`. Until you tell JPA "these are two sides of a relationship, linked through the
`order_id` column", the entities are not valid.
:::

:::step{type=task task=order_items title="Your turn: map orders and their items"}
1. In **`OrderItem.java`**, map the `order` field as the **many** side of the relationship, with the foreign
   key column **`order_id`**.
2. In **`CustomerOrder.java`**, map the `items` list as the **one** side: mapped by the `order` field of
   `OrderItem`, with all operations cascading to the items.

The annotations come from `jakarta.persistence`. Rebuild and run, then ask for Asha's order:

```bash run
curl localhost:8080/orders/1
```

```text
{"id":1,"customer":"Asha","items":2,"totalPaise":9400}
```

Two items: 2 x Rs 20 + 3 x Rs 18 = Rs 94. Press **Check**.
:::

:::step{type=concept title="Lazy loading: items arrive when you touch them"}
When JPA loads an order, does it also load its items? By default, for a `@OneToMany` list: **no**. The list is
**lazy**. JPA puts a placeholder in `items`, and only when your code first *uses* it (`order.getItems().size()`,
a loop over it) does JPA run a second query to fetch them.

That is usually a good idea. If a screen only shows customer names, loading every item of every order would
be wasted work.

There is one condition: the lazy loading needs an open connection to the database (a **persistence context**,
JPA's working session) at the moment you touch the list. That is why `OrderService`'s methods are marked
`@Transactional(readOnly = true)`: the session stays open for the whole method, so the items can still be
loaded inside it. Touch a lazy list after the session is closed, and you get the infamous
`LazyInitializationException`. (Chapter 23 is all about `@Transactional`; for now, read it as "keep the database
session open for this method".)
:::

:::step{type=example title="The N+1 problem, in the SQL log"}
Lazy loading has a trap. Look at `OrderService.summaries()`:

```java
return repository.findAll().stream().map(OrderService::toSummary).toList();
```

and `toSummary` calls `o.getItems()` for each order. Run the app with SQL logging, and ask for all orders:

```bash run
java -jar target/relationships.jar --spring.jpa.show-sql=true
```

```bash run
curl localhost:8080/orders
```

Count the queries in the log:

```text
Hibernate: select co1_0.id,co1_0.customer from orders co1_0
Hibernate: select ... from order_item i1_0 where i1_0.order_id=?
Hibernate: select ... from order_item i1_0 where i1_0.order_id=?
Hibernate: select ... from order_item i1_0 where i1_0.order_id=?
Hibernate: select ... from order_item i1_0 where i1_0.order_id=?
Hibernate: select ... from order_item i1_0 where i1_0.order_id=?
```

**One** query for the orders, then **one more per order**, as each order's lazy list is touched. Five orders,
six queries. That is **N+1**: N orders, plus 1.

Six queries sounds harmless. But each one is a round trip to the database server, typically a millisecond or
more over the network. With 500 orders on an admin page, it is 501 round trips, and the page takes seconds. The
Java code looks the same either way, which is why this problem hides so well. The SQL log is how you see it.
:::

:::step{type=concept title="The fix: JOIN FETCH in one query"}
The fix is to tell JPA, for this particular use: "load the orders **and** their items **together**, in one
query". That is a **join**, and in JPA you ask for it with **`JOIN FETCH`** in a query you write yourself.

You write it with **`@Query`** on a repository method, in **JPQL** (the JPA query language). JPQL looks like
SQL, but talks about **entities and fields**, not tables and columns:

```java
@Query("select distinct p from Post p join fetch p.comments")
List<Post> findAllWithComments();
```

- `select p from Post p`: "posts" (the entity `Post`, called `p`).
- `join fetch p.comments`: "and fetch each post's `comments` in the same query".
- `distinct`: a join returns one row per comment, so a post with three comments would appear three times;
  `distinct` removes the duplicates from the result list.

Hibernate turns it into one SQL `select ... from post join comment on ...`, and every post comes back with its
comments already loaded. No lazy loading, no extra queries.
:::

:::step{type=task task=fix_n_plus_one title="Your turn: one query for the order list"}
1. In `OrderRepository`, add a method with a `@Query` that loads **every order with its items** using
   `join fetch` (and `distinct`). (`Query` is `org.springframework.data.jpa.repository.Query`.)
2. In `OrderService.summaries()`, call it instead of `findAll()`.

Rebuild, run with `--spring.jpa.show-sql=true`, and request `/orders` again. Now there is **one** query:

```text
Hibernate: select distinct co1_0.id,co1_0.customer,i1_0.order_id,i1_0.id,... from orders co1_0 join order_item i1_0 on co1_0.id=i1_0.order_id
```

Same JSON answer, one round trip instead of six. The check counts the SQL statements. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In a one-to-many between Order and OrderItem, which table has the foreign key column?
:::
- [ ] orders
- [x] order_item
- [ ] A third table
:::explain
The link lives on the "many" side: each item row stores its order's id. That is why `@JoinColumn` goes on
`OrderItem.order`, and `mappedBy` on `CustomerOrder.items`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A page lists 200 orders and shows each order's item count, using `findAll()` and lazy items. How many queries run?
:::
- [ ] 1
- [ ] 2
- [x] 201
:::explain
One for the orders, then one per order when its items are touched: N+1. A `join fetch` query makes it one.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `mappedBy = "order"` on `CustomerOrder.items` say?
:::
- [ ] Create a column called order in the orders table
- [x] This list is the same relationship as the order field in OrderItem, which owns the foreign key
- [ ] Sort the items by order
:::explain
Without `mappedBy`, JPA would treat the list as a second, separate relationship (and create a join table for
it). With it, both sides describe one link: the `order_id` column.
:::
:::

:::step{type=deep-dive title="Go deeper: EAGER, entity graphs, and returning entities as JSON"}
**Why not make it EAGER?** `@OneToMany(fetch = FetchType.EAGER)` loads items every time an order is loaded,
everywhere, even where nobody needs them, and often still with extra queries. Keep relationships lazy, and fetch
what each use case needs (`join fetch`, or `@EntityGraph(attributePaths = "items")` on a repository method).

**@ManyToOne is eager by default.** The other direction (an item loading its order) is eager unless you write
`@ManyToOne(fetch = FetchType.LAZY)`, which is a good habit on large models.

**Never return entities with relationships as JSON.** Jackson would follow `order.items`, then `item.order`,
then `order.items`... forever (or until a stack overflow), and touch lazy lists outside the session. That is why
this project returns an `OrderSummary` DTO (chapter 12): you decide exactly what is loaded and sent.
:::

:::step{type=recap title="What you can do now"}
You can now map and load related data, efficiently:

- A **foreign key** column on the "many" side links rows: one order, many items.
- **`@ManyToOne` + `@JoinColumn(name = "...")`** on the owning (many) side; **`@OneToMany(mappedBy = "...")`** on
  the other; **`cascade = CascadeType.ALL`** to save and delete them together.
- Collections are **lazy**: loaded when first touched, inside an open session (`@Transactional`).
- **N+1**: a list of N entities plus one query per entity for a lazy relationship. Spot it in the SQL log.
- Fix it with **`@Query("select distinct o from Order o join fetch o.items")`** (JPQL talks about entities and fields).
- Return **DTOs**, not entities with relationships.

Next, chapter 22: when there are thousands of products, nobody wants them all at once. Paging, sorting and your own queries.
:::
