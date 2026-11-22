:::step{type=story title="Thousands of products"}
The Shop API's catalogue will not stay at six products. A real shop has thousands, a marketplace millions.
`GET /products` returning **all** of them would send megabytes of JSON, make the database read every row, and
make the phone app freeze while it draws a list nobody scrolls to the end of. Every shopping app you have used
shows products **a page at a time**, sorted by what you chose.

Spring Data makes paging and sorting almost free: one parameter, and the database returns exactly one page. This
chapter adds that, and then teaches you to write your own queries when a method name is not enough: **JPQL**
with `@Query`.

:::mission
Serve products a page at a time with sorting, and write a price-range query in JPQL.
:::
:::

:::step{type=concept title="Paging in the database: offset and limit"}
To return page 2 of a list sorted by name, with 20 items per page, the database needs three instructions:
**sort** by name, **skip** the first 20 rows (page 1), and **return** the next 20. In SQL:

```sql
select ... from product order by name offset 20 rows fetch first 20 rows only
```

The skip is the **offset**, the size is the **limit**. The important part: the database does it. Only 20 rows
leave the database, however many products there are.

There is one more thing a client usually wants: **how many pages are there in total?** (To show "page 2 of 47".)
That needs a second, cheap query: `select count(...) from product`.

Pages are numbered **from 0** in Spring Data: `page=0` is the first page. Keep that in mind; it surprises
everyone once.
:::

:::step{type=concept title="Pageable and Page"}
Spring Data wraps all of that in two types:

- **`Pageable`**: "which page, how big, sorted how". It is the *question*.
- **`Page<T>`**: one page of results, plus the totals. It is the *answer*.

Every `JpaRepository` already has `findAll(Pageable pageable)`. And here is the nice part: if a controller
method has a **`Pageable` parameter**, Spring **builds it from the query string for you**:

```java
@GetMapping("/customers")
public Page<Customer> list(Pageable pageable) {
    return customers.findAll(pageable);
}
```

```text
GET /customers?page=0&size=20&sort=name           first 20, by name
GET /customers?page=3&size=10&sort=city,desc      page 4 of 10 per page, by city Z to A
GET /customers                                    defaults: page 0, size 20, unsorted
```

`sort` takes a field name, and optionally `,asc` or `,desc`. You can even repeat it:
`sort=city&sort=name` sorts by city, then by name within each city.
:::

:::step{type=try title="Today: everything, every time" file="22-paging/src/main/java/com/shop/product/ProductController.java" line="18-23"}
`ProductController.all()`, on the right, returns `findAll()`: every product. Run the app with SQL logging and
ask for "page 1 of size 2":

```bash run
cd 22-paging && mvn -q -o package -DskipTests && java -jar target/paging.jar --spring.jpa.show-sql=true
```

```bash run
curl "localhost:8080/products?page=1&size=2&sort=name"
```

All six products come back, unsorted. The parameters are ignored, because nothing in the method reads them.
:::

:::step{type=task task=paged_products title="Your turn: products a page at a time"}
Change `all()` so it takes a **`Pageable`** parameter and returns a **`Page<Product>`** from
`repository.findAll(pageable)`. (Imports: `org.springframework.data.domain.Page` and `Pageable`.)

Rebuild, run, and ask for the second page of two, by name:

```bash run
curl "localhost:8080/products?page=1&size=2&sort=name"
```

```text
{"content":[{"id":4,"name":"Kachori",...},{"id":1,"name":"Mango lassi",...}],
 "page":{"size":2,"number":1,"totalElements":6,"totalPages":3}}
```

Read the answer: `content` is the page (Kachori and Mango lassi: positions 3 and 4 by name, because page 0 held
Bhel puri and Filter coffee), and `page` tells the client everything it needs for a pager: 6 products, 3 pages,
this is number 1. And in the log, the two queries from the first step:

```text
Hibernate: select ... from product p1_0 order by p1_0.name offset ? rows fetch first ? rows only
Hibernate: select count(p1_0.id) from product p1_0
```

Press **Check**.
:::

:::step{type=concept title="When a name is not enough: @Query and JPQL"}
Derived queries (chapter 20) cover most simple questions. For anything more, you write the query yourself, with
**`@Query`** on a repository method. You already used one for `join fetch` in chapter 21.

The language is **JPQL** (Jakarta Persistence Query Language). It looks like SQL, with one big difference: it
talks about your **entities and their fields**, not tables and columns:

```java
@Query("select c from Customer c where c.city = :city and c.joinedOn >= :since order by c.name")
List<Customer> joinedRecently(@Param("city") String city, @Param("since") LocalDate since);
```

- `from Customer c`: the **entity** `Customer` (not the table `customer`), with a short name `c`.
- `c.city`, `c.joinedOn`: entity **fields**, in Java's camelCase (Hibernate maps `joinedOn` to `joined_on`).
- `:city`, `:since`: **named parameters**. `@Param("city")` connects each method parameter to its name.
- `select c`: return whole `Customer` entities.

Why not plain SQL? JPQL keeps working if you rename a column (you only change the entity mapping), it is checked
when the app starts (a misspelt field stops the start-up), and Hibernate translates it for whichever database you
use. (For the rare query only plain SQL can express, `@Query(value = "...", nativeQuery = true)` exists.)

Never build a query by gluing strings with user input: `"... where city = '" + city + "'"`. That is how **SQL
injection** happens. Parameters (`:city`) are always passed safely, separately from the query text.
:::

:::step{type=task task=price_range title="Your turn: a price range in JPQL"}
1. In `ProductRepository`, write a method **`inPriceRange(int min, int max)`** with a `@Query`: the products
   whose price is **between** `min` and `max` (both included), **cheapest first**. Use named parameters and
   `@Param`. (Imports: `org.springframework.data.jpa.repository.Query`, `org.springframework.data.repository.query.Param`,
   `java.util.List`.)
2. In `ProductController.priceRange`, return its result.

Hint for JPQL: `between ... and ...` includes both ends, and the entity's field is `pricePaise`.

Rebuild, run, and try:

```bash run
curl "localhost:8080/products/price-range?min=2000&max=3000"
```

You should get Mango lassi (2000), Kachori (2200), Vada pav (2500) and Filter coffee (3000), in that order. The log
shows your JPQL, translated:

```text
Hibernate: select ... from product p1_0 where p1_0.price_paise between ? and ? order by p1_0.price_paise
```

Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A client wants the first 10 products. Which request?
:::
- [x] /products?page=0&size=10
- [ ] /products?page=1&size=10
- [ ] /products?size=10&page=first
:::explain
Spring Data numbers pages from 0. `page=1` would be products 11 to 20.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In `@Query("select p from Product p where p.pricePaise < :max")`, what is `p.pricePaise`?
:::
- [ ] A column of the product table
- [x] A field of the Product entity (Hibernate maps it to the price_paise column)
- [ ] A parameter
:::explain
JPQL talks about entities and fields. Hibernate translates them to tables and columns.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does a paged request run two queries?
:::
- [ ] One for each page
- [x] One for the page's rows, one count for the total number of elements and pages
- [ ] Spring Data always runs every query twice
:::explain
The rows come with offset and limit; the totals need a `count`. If the client does not need totals (infinite
scroll), a `Slice` instead of a `Page` skips the count.
:::
:::

:::step{type=deep-dive title="Go deeper: page size limits, Slice, and keyset paging"}
**Limit the size.** Without a limit, a client can ask for `size=1000000`. Spring Boot lets you cap it:
`spring.data.web.pageable.max-page-size=100`. Set a default with `spring.data.web.pageable.default-page-size`.

**Slice.** Return `Slice<T>` instead of `Page<T>` to skip the count query: you only learn whether there is a next
page. Good for infinite scrolling.

**Deep pages are slow.** `offset 100000` still makes the database walk past 100,000 rows. For huge tables, APIs
use **keyset paging**: "the next 20 after id 4711" (`where id > :last order by id`), which stays fast at any
depth. You will meet it in the production course.

**Pageable with your own queries.** A `@Query` method can also take a `Pageable` and return a `Page`; Spring Data
adds the sorting, offset and limit to your JPQL.
:::

:::step{type=recap title="What you can do now"}
Your API can now serve big catalogues:

- **Paging** is done by the database: `order by`, **offset**, **limit**; plus a `count` for the totals.
- A **`Pageable`** controller parameter is built from `?page=` (from 0), `&size=` and `&sort=field,asc|desc`;
  `findAll(pageable)` returns a **`Page<T>`**: `content` plus size, number, totalElements, totalPages.
- **`@Query`** with **JPQL** writes your own queries about entities and fields, with **named parameters**
  (`:name` + `@Param`), checked at start-up, safe from SQL injection.

:::photo{src="/lesson-images/spring/spring-22-notes.webp" alt="Handwritten notes about Paging: the database pages: limit, offset, Pageable from ?page=&size=&sort=, page numbers start at 0, @Query with JPQL, named parameters: :name" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 23: when one action changes several rows, they must all succeed or all fail. Transactions.
:::
