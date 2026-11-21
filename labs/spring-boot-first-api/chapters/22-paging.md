:::step{type=story title="Why this chapter"}
A shop has thousands of products. Returning all of them in one response is slow for the server, slow
for the network and useless for a screen that shows twenty. This chapter returns data a page at a time,
sorted, and writes a custom query when a method name is not enough.

:::mission
In the `22-paging` folder: return products a page at a time, and add a price-range query with `@Query`.
:::
:::

:::step{type=concept title="Pageable and Page"}
Spring Data can read paging from the request and apply it in SQL:

```java
@GetMapping("/products")
public Page<Product> all(Pageable pageable) {
    return repository.findAll(pageable);
}
```

`GET /products?page=1&size=20&sort=name` fills the `Pageable` (pages start at 0). The query gets
`ORDER BY name LIMIT 20 OFFSET 20`, plus a `COUNT(*)` for the total. The `Page` result holds the content
and the numbers a client needs to show page links:

```json
{"content": [ ... ], "page": {"size": 20, "number": 1, "totalElements": 1430, "totalPages": 72}}
```
:::

:::step{type=example title="Worked example: page 2 of 3"}
Six products, `size=2`, `sort=name`:

:::trace{title="GET /products?page=1&size=2&sort=name"}
| step | value | note |
|---|---|---|
| sorted by name | Bhel puri, Filter coffee, Kachori, Masala tea, Samosa, Vada pav | ORDER BY name |
| OFFSET page * size | skip 1 * 2 = 2 rows | Page 0 would be the first two. |
| LIMIT size | take 2 rows | |
| content | Kachori, Masala tea | The second page. |
| COUNT(*) | totalElements 6, totalPages 3 | A second query, for the page links. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`GET /products?page=0&size=5` on 12 products. How many products are in `content`, and what is `totalPages`?
:::
- [x] 5 products, 3 pages
- [ ] 12 products, 1 page
- [ ] 5 products, 2 pages
:::explain
Pages start at 0, each holds up to 5. 12 products need 3 pages: 5, 5 and 2.
:::
:::

:::step{type=try title="Ask for a page"}
```bash run
cd 22-paging && mvn -q -o package -DskipTests && java -jar target/paging.jar
```

After the first task, in a second tab:

```bash run
curl -s "localhost:8080/products?page=0&size=2&sort=pricePaise,desc"; echo
```

`sort=property,desc` sorts the other way.
:::

:::step{type=task task=paged_products title="Warm-up: products a page at a time"}
In `22-paging`, change `GET /products` to take a `Pageable` parameter and return
`repository.findAll(pageable)` as a `Page<Product>`.
:::

:::step{type=concept title="@Query with JPQL"}
When a method name gets long, write the query yourself in **JPQL**, a query language over entities
(class and field names, not tables and columns):

```java
@Query("select p from Product p where p.pricePaise between :min and :max order by p.pricePaise")
List<Product> inPriceRange(@Param("min") int min, @Param("max") int max);
```

`:min` and `:max` are named parameters, filled from the `@Param` arguments. Values are always passed as
parameters, never pasted into the query text, which prevents SQL injection. JPQL is checked at start-up,
like derived query names.
:::

:::step{type=task task=price_range title="A price range with @Query"}
Add `inPriceRange(int min, int max)` to `ProductRepository` with an `@Query`: products whose price is
between `min` and `max` (both included), cheapest first. Use it in `GET /products/price-range`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
In JPQL, what does `Product` in `select p from Product p` refer to?
:::
- [ ] The table `product`
- [x] The entity class `Product`
- [ ] A Java variable named `Product`
:::explain
JPQL uses entity and field names; Hibernate translates them to table and column names.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why page in the database instead of loading everything and using `subList` in Java?
:::
- [ ] Java cannot sort lists
- [x] The database sends only the rows of one page, instead of every row over the network and into memory
- [ ] `subList` is not allowed in controllers
:::explain
With `LIMIT` and `OFFSET`, the database does the work and transfers 20 rows instead of thousands.
:::
:::

:::step{type=deep-dive title="Deep pages and limits"}
`OFFSET 100000` still makes the database walk past 100,000 rows, so very deep pages get slow. Large
lists use **keyset paging** instead: "the next 20 after the last id I saw" (`WHERE id > ? ORDER BY id`).
Also cap the page size (`spring.data.web.pageable.max-page-size`, default 2000), so a client cannot ask
for a million rows in one page.
:::

:::step{type=recap title="Chapter done"}
- `Pageable` reads `page`, `size` and `sort` from the request; `Page` returns content plus totals.
- Paging and sorting run in SQL (`LIMIT`, `OFFSET`, `ORDER BY`), with a `COUNT` for the totals.
- `@Query` with JPQL and named parameters handles queries a method name cannot express.
:::
