:::step{type=story title="Why this chapter"}
Data is connected: an order has items, an item belongs to an order. JPA maps these connections to
foreign keys, so `order.getItems()` loads the related rows for you. It also hides a classic performance
trap, the **N+1 query problem**, which this chapter shows you how to see and fix.

:::mission
In the `13-relationships` folder: map orders and their items, then load a list of orders with one query
instead of six.
:::
:::

:::step{type=concept title="@ManyToOne and @OneToMany"}
In the database, the connection is one column: `order_item.order_id` points to `orders.id`. In Java, both
sides can see it:

```java
// OrderItem: many items belong to one order. This side owns the foreign key.
@ManyToOne
@JoinColumn(name = "order_id")
private CustomerOrder order;

// CustomerOrder: one order has many items, mapped by the field "order" in OrderItem.
@OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
private List<OrderItem> items = new ArrayList<>();
```

`mappedBy` says the other side owns the column, so it is not mapped twice. `cascade = ALL` saves and
deletes items together with their order.

:::diagram{name="one-to-many"}
The foreign key is in the item table; both classes can navigate it.
:::
:::

:::step{type=concept title="Lazy loading"}
By default `@OneToMany` is **lazy**: loading an order does not load its items. The items are loaded the
first time code calls `getItems()`, with a separate query. That saves work when items are not needed, but
it must happen inside a transaction (`@Transactional` on the service method), while the database
session is still open.

The cost appears with lists. Loading 5 orders is one query; touching each order's items adds one query per
order: 1 + 5 = 6 queries. With 500 orders, 501 queries. This is the **N+1 problem**.
:::

:::step{type=example title="Worked example: counting the queries"}
:::trace{title="listing 3 orders with lazy items"}
| code | SQL sent | queries so far | note |
|---|---|---|---|
| repository.findAll() | SELECT * FROM orders | 1 | One query for all the orders. |
| order 1: getItems().size() | SELECT * FROM order_item WHERE order_id = 1 | 2 | Lazy: the items load only now. |
| order 2: getItems().size() | SELECT * FROM order_item WHERE order_id = 2 | 3 | Another query, for another order. |
| order 3: getItems().size() | SELECT * FROM order_item WHERE order_id = 3 | 4 | N orders cost N + 1 queries. |
:::

The fix loads the orders and their items in one query with `JOIN FETCH`:

```java
@Query("select distinct o from CustomerOrder o join fetch o.items")
List<CustomerOrder> findAllWithItems();
```
:::

:::step{type=predict title="Guess first"}
:::question
An endpoint lists 200 orders and shows each one's item count. With lazy items and `findAll()`, how many queries run?
:::
- [ ] 1
- [ ] 2
- [x] 201
:::explain
One query for the orders, then one per order for its items. `JOIN FETCH` brings it down to one.
:::
:::

:::step{type=try title="Start it"}
```bash run
cd 13-relationships && mvn -q -o package -DskipTests && java -jar target/relationships.jar 2>&1 | grep -m3 -E "Started|Caused by"
```

Until the relationship is mapped, Hibernate cannot store a `CustomerOrder` field in a column, and the
application does not start.
:::

:::step{type=task task=order_items title="Warm-up: map orders and items"}
In `13-relationships`: map `OrderItem.order` with `@ManyToOne` and `@JoinColumn(name = "order_id")`, and
`CustomerOrder.items` with `@OneToMany(mappedBy = "order", cascade = CascadeType.ALL)`.

`GET /orders/1` then shows 2 items totalling 9400 paise.
:::

:::step{type=task task=fix_n_plus_one title="One query for the order list"}
`GET /orders` runs 6 queries for 5 orders. Add `findAllWithItems()` with a `JOIN FETCH` query to
`OrderRepository`, and use it in `OrderService.summaries()`.

The check counts the SQL statements Hibernate sends.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which side of a one-to-many relationship holds the foreign key column?
:::
- [ ] The "one" side (`orders`)
- [x] The "many" side (`order_item.order_id`)
- [ ] A separate join table, always
:::explain
Each item row stores which order it belongs to. That is why `@ManyToOne` owns the mapping and
`@OneToMany` uses `mappedBy`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why return a DTO such as `OrderSummary` instead of the `CustomerOrder` entity from the controller?
:::
- [ ] Entities cannot be converted to JSON
- [x] The order points to its items and each item back to the order, so JSON conversion would loop, and lazy data may not be loaded
- [ ] DTOs are faster to query
:::explain
Bidirectional relationships make naive JSON conversion recurse forever, and lazy collections may fail
outside a transaction. Mapping to a DTO inside the service avoids both.
:::
:::

:::step{type=deep-dive title="Seeing the SQL"}
`spring.jpa.show-sql=true` prints every statement, and `logging.level.org.hibernate.SQL=debug` does the
same through the logger. In tests, Hibernate's statistics (`hibernate.generate_statistics=true`) count
statements precisely, which is how this chapter's check measures your fix. Other fixes for N+1:
`@EntityGraph(attributePaths = "items")` on a repository method, or batch fetching
(`hibernate.default_batch_fetch_size`), which loads lazy collections in groups.
:::

:::step{type=recap title="Chapter done"}
- `@ManyToOne` with `@JoinColumn` owns the foreign key; `@OneToMany(mappedBy = ...)` is the other side.
- Collections are lazy: they load on first access, inside a transaction.
- Lists with lazy collections cause N+1 queries; `JOIN FETCH` loads everything in one.
- Return DTOs from controllers, not entities with relationships.
:::
