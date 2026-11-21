:::step{type=story title="Why this chapter"}
Real queries filter: products in a category, an order by its number, whether an email is already used.
Spring Data JPA can write those queries from a method's name, so most repositories contain only method
declarations. This chapter shows how the naming works, and how to use it to keep data consistent.

:::mission
In the `20-repositories` folder: list products by category with a derived query, and refuse duplicate
SKUs with a 409.
:::
:::

:::step{type=concept title="Derived queries"}
Spring Data reads a repository method's name and builds the query from it:

```java
List<Product> findByCategory(String category);
// SELECT ... FROM product WHERE category = ?

List<Product> findByCategoryOrderByNameAsc(String category);
// ... WHERE category = ? ORDER BY name ASC

List<Product> findByPricePaiseLessThan(int max);
// ... WHERE price_paise < ?

boolean existsBySku(String sku);
// SELECT ... WHERE sku = ? (stops at the first match)
```

The name is `find`, `exists`, `count` or `delete`, then `By`, then property names with keywords such as
`And`, `Or`, `LessThan`, `Between`, `Containing`, `OrderBy`. A misspelled property name stops the
application at start-up, so mistakes are found early.
:::

:::step{type=example title="Worked example: customers by city"}
```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {
    List<Customer> findByCityOrderByNameAsc(String city);       // 1
    long countByCity(String city);                              // 2
    Optional<Customer> findByEmail(String email);               // 3
}
```

1. All customers in a city, sorted by name: a `WHERE` and an `ORDER BY`.
2. Only the number, computed by the database (`COUNT(*)`), not by loading rows.
3. At most one result: `Optional` makes "not found" explicit.

The service calls these like normal methods; the SQL runs in the database.
:::

:::step{type=predict title="Guess first"}
:::question
What query does `findByCategoryAndPricePaiseLessThan(String c, int p)` run?
:::
- [ ] `WHERE category = ? OR price_paise < ?`
- [x] `WHERE category = ? AND price_paise < ?`
- [ ] It fails: names cannot combine two properties
:::explain
`And` joins the two conditions, and parameters are matched in order: `c` to category, `p` to the price.
:::
:::

:::step{type=try title="Filter in the database"}
```bash run
cd 20-repositories && mvn -q -o package -DskipTests && java -jar target/repositories.jar
```

After the first task, in a second tab:

```bash run
curl -s "localhost:8080/products?category=snacks"; echo
```
:::

:::step{type=task task=find_by_category title="Warm-up: products by category"}
In `20-repositories`, add `findByCategoryOrderByNameAsc(String category)` to `ProductRepository`, and use
it in `GET /products` when a `category` parameter is given. Without the parameter, return all products.
:::

:::step{type=concept title="Check before you save"}
Some rules depend on data already stored: a SKU must be unique. Check it with a cheap query before
saving, and answer with a clear status:

```java
if (repository.existsBySku(body.sku())) {
    return ResponseEntity.status(HttpStatus.CONFLICT).build();   // 409
}
```

`existsBy...` stops at the first match and returns no row data, so it is cheaper than `findBy...`. The
unique constraint from chapter 11 still matters: two requests at the same instant could both pass the
check, and the constraint stops the second.
:::

:::step{type=task task=sku_conflict title="409 for a duplicate SKU"}
Add `existsBySku(String sku)` to `ProductRepository`. In `POST /products`, answer `409 Conflict` without
saving when the SKU exists; otherwise create the product as before (201).
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which return type fits "the customer with this email, if any"?
:::
- [ ] `List<Customer>`
- [x] `Optional<Customer>`
- [ ] `Customer`, or an exception
:::explain
`Optional` says "zero or one" in the type, so callers must handle the missing case.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`findByNmae(String name)` has a typo. When is it found?
:::
- [x] At start-up: Spring cannot find a property `nmae` and refuses to start
- [ ] On the first call
- [ ] Never: it returns an empty list
:::explain
Spring Data parses method names at start-up and checks them against the entity.
:::
:::

:::step{type=deep-dive title="When names get too long"}
`findByCategoryAndPricePaiseBetweenAndNameContainingIgnoreCaseOrderByPricePaiseAsc` works, but nobody
wants to read it. For complex queries use `@Query` with JPQL (next chapter), or Specifications for
filters built at run time. A good rule: derived queries for one or two conditions, `@Query` beyond that.
:::

:::step{type=recap title="Chapter done"}
- Spring Data builds queries from method names: `findBy`, `existsBy`, `countBy`, with `And`, `LessThan`, `OrderBy`.
- Method names are checked at start-up against the entity's properties.
- Check stored data with `existsBy...` and answer 409; keep the database constraint as the final guard.
:::
