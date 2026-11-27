:::step{type=story title="Asking the database questions"}
`findAll` and `findById` are a start, but real screens ask more specific questions: "all the snacks, A to Z",
"is this SKU already taken?", "customers who signed up this week". You could fetch everything with
`findAll()` and filter in Java, but with a real catalogue of a hundred thousand products, that would drag every
row over the network to keep twenty. The database is built to answer exactly these questions quickly, with
**indexes** (sorted lookup lists, like the index at the back of a book, that let it find matching rows without
reading every row). You just have to ask it.

Spring Data has a trick that feels like magic the first time and is completely logical once you see it:
you **name a method** in the repository interface, and Spring Data **writes the query from the name**. This
chapter teaches that naming language, and uses it to fix a 500 error that the database constraint from
chapter 19 is now causing.

:::mission
List products by category with a derived query, and answer 409 for a duplicate SKU instead of 500.
:::
:::

:::step{type=concept title="Derived queries: a method name is a query"}
Add this method to a repository interface, with **no code**:

```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    List<Customer> findByCity(String city);
}
```

At start-up, Spring Data reads the method's name and builds the query for you:

```text
findByCity("Pune")   ->   select ... from customer where city = ?   (with ? = 'Pune')
```

It splits the name into parts: **`find`** (fetch entities) **`By`** (here come the conditions) **`City`** (a
field of `Customer`, compared with the first parameter). The field must exist in the entity, with exactly that
name (capitalised). A typo, like `findByCitty`, is caught **at start-up** with a clear error ("No property 'citty' found for type
'Customer'"; we tried such a typo on our lab machine and got exactly that wording), not later when a customer
clicks something.

That is what **derived queries** are: the query is derived from the method name. You declare what you want;
Spring Data writes the SQL.
:::

:::step{type=concept title="The naming language"}
You can combine many pieces. Here are the ones you will use most, all on `Customer`:

```java
List<Customer> findByCityAndActive(String city, boolean active);      // where city = ? and active = ?
List<Customer> findByCityOrState(String city, String state);         // where city = ? or state = ?
List<Customer> findByAgeGreaterThan(int age);                        // where age > ?
List<Customer> findByAgeBetween(int from, int to);                   // where age between ? and ?
List<Customer> findByNameContainingIgnoreCase(String part);          // where lower(name) like %part%
List<Customer> findByEmailIsNull();                                  // where email is null
List<Customer> findByCityOrderByNameAsc(String city);                // ... order by name asc
Optional<Customer> findByEmail(String email);                        // at most one result
boolean existsByEmail(String email);                                 // is there at least one?
long countByCity(String city);                                       // how many?
```

Read each name as an English sentence and you have the query. The **return type** matters too:

- `List<Customer>`: any number of results.
- `Optional<Customer>`: zero or one (and an error if the database finds two).
- `boolean` with `existsBy...`: just yes or no. Very cheap: the database stops at the first match.
- `long` with `countBy...`: a number.

Parameters are matched **in order**: the first parameter goes to the first condition in the name, and so on.
:::

:::step{type=try title="The project" file="20-repositories/src/main/java/com/shop/product/ProductRepository.java" line="5-10"}
`ProductRepository` is on the right, with two TODOs. Products now have a **category** (`sweets` or
`snacks`), and `data.sql` loads five of them. The controller's `GET /products` takes an optional `category`
parameter, but ignores it for now.

Start the app with SQL logging on, so you can see every query Hibernate runs:

```bash run
cd 20-repositories && mvn -q -o package -DskipTests && java -jar target/repositories.jar --spring.jpa.show-sql=true
```

```bash run
curl "localhost:8080/products?category=snacks"
```

All five products come back, sweets included (on our lab machine the answer started with the Mango kulfi), and the
log shows one plain `select ... from product`.
:::

:::step{type=task task=find_by_category title="Your turn: products by category, A to Z"}
1. In `ProductRepository`, declare a derived query that returns the products **of one category, sorted by
   name ascending**. (Look at the naming list: you need `findBy`, the field, and `OrderBy...Asc`.)
2. In `ProductController.list`, call it when a `category` is given, and `findAll()` when it is not.

Rebuild, run, and ask again:

```bash run
curl "localhost:8080/products?category=snacks"
```

On our lab machine:

```text
[{"id":5,"name":"Bhel puri","pricePaise":4000,"category":"snacks","sku":"BHE-1"},{"id":4,"name":"Kachori","pricePaise":2200,"category":"snacks","sku":"KAC-1"},{"id":3,"name":"Samosa","pricePaise":1800,"category":"snacks","sku":"SAM-1"}]
```

And the log shows the database doing the work:

```text
Hibernate: select p1_0.id,p1_0.category,p1_0.name,p1_0.price_paise,p1_0.sku from product p1_0 where p1_0.category=? order by p1_0.name
```

(`p1_0` is a short name Hibernate gives the table inside the query; the `?` is filled with `snacks` when the query
runs.) Only the snacks crossed from the database to Java. Press **Check**.

Usual slips: `OrderBy` placed before `By` (the conditions come first), or calling the new method even when no
category was given (then nothing matches `null`, and the list is empty).
:::

:::step{type=example title="Why duplicate SKUs cause a 500 now"}
Chapter 19 made `sku` unique in the database. Now see what happens when a client creates a product with a SKU
that is already taken:

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Kulfi again", "pricePaise": 1000, "category": "sweets", "sku": "KUL-1"}'
```

```text
HTTP/1.1 500
{"timestamp":"...","status":500,"error":"Internal Server Error","path":"/products"}
```

And in the server log, deep in the stack trace:

```text
Unique index or primary key violation: "PUBLIC.CONSTRAINT_INDEX_1 ON PUBLIC.PRODUCT(SKU NULLS FIRST) VALUES ( /* 1 */ 'KUL-1' )"
```

(That is H2's wording, from our lab machine. PostgreSQL or MySQL would say the same thing in their own words.)

The good news: the database protected the data, as designed. Nothing was saved. The bad news: the **client**
is told "the server broke" (500), when actually the client asked for something that conflicts with existing
data. That is a **409 Conflict**, and the client deserves to know which.

The constraint is the safety net. In the normal case, the application should check first and give a clear
answer.
:::

:::step{type=concept title="Check first, with existsBy"}
The clean pattern is: before saving, **ask** whether the SKU exists, and refuse politely if it does.

```java
@PostMapping("/customers")
public ResponseEntity<Customer> create(@RequestBody NewCustomer body) {
    if (customers.existsByEmail(body.email())) {
        return ResponseEntity.status(HttpStatus.CONFLICT).build();        // 409, nothing saved
    }
    Customer saved = customers.save(new Customer(body.name(), body.email()));
    return ResponseEntity.created(URI.create("/customers/" + saved.getId())).body(saved);
}
```

`existsByEmail` becomes a tiny query. For this chapter's `existsBySku`, our lab machine's log showed:

```text
select p1_0.id from product p1_0 where p1_0.sku=? fetch first ? rows only
```

"Fetch first rows only": the database stops at the first match. It does not load the whole customer, only
checks that one exists. Cheap and fast.

And the database constraint stays, as the net under the trapeze: if two requests with the same SKU arrive at
exactly the same instant, both may pass the check, and then the constraint stops the second one. (Turning that
rare case into a 409 as well is what an exception handler from chapter 17 is for.)
:::

:::step{type=task task=sku_conflict title="Your turn: 409 for a duplicate SKU"}
1. In `ProductRepository`, declare a derived query that answers **whether a product with a given SKU exists**.
2. In `ProductController.create`, answer **409 Conflict** (without saving) when it does.

Rebuild, run, and try the duplicate again, then a new SKU:

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Kulfi again", "pricePaise": 1000, "category": "sweets", "sku": "KUL-1"}'
```

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Rasmalai", "pricePaise": 4500, "category": "sweets", "sku": "RAS-1"}'
```

`409`, then `201` (that is what our lab machine answered). Press **Check**.

Usual slips: `findBySku` returning a product and testing it for `null` (it works, but loads the whole row; `existsBy`
asks only yes or no), or saving first and checking after (then the duplicate reaches the database and you are back
to the 500).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `List<Order> findByStatusAndTotalPaiseGreaterThan(String status, int min)` run?
:::
- [ ] where status = ? or total_paise > ?
- [x] where status = ? and total_paise > ?
- [ ] It does not compile: names that long are not allowed
:::explain
`And` joins the two conditions; `GreaterThan` compares with `>`. Parameters fill the conditions in order.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
You declare `findByCatgory(String c)` (a typo). When do you find out?
:::
- [ ] When a customer requests the category list
- [x] At start-up: Spring Data reports that Product has no property catgory
- [ ] Never: it returns an empty list
:::explain
Derived queries are checked against the entity when the app starts. A wrong name stops the start-up, which is
exactly when you want to find out.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why check with `existsBySku` first, if the unique constraint already stops duplicates?
:::
- [ ] The constraint does not work with H2
- [x] So the client gets a clear 409 instead of a 500; the constraint remains the safety net
- [ ] existsBy is required before every save
:::explain
Both layers have a job: the check gives a good answer in the normal case; the constraint guarantees the data
even in the rare race.
:::
:::

:::step{type=deep-dive title="Go deeper: when names get too long"}
Derived queries are perfect for simple questions. When a name grows past three or four conditions
(`findByCategoryAndPricePaiseBetweenAndActiveTrueOrderByNameAsc`), it becomes hard to read. Then write the
query yourself with **`@Query`** and JPQL, which chapter 22 introduces. For searches with many optional filters
(a filter form with ten fields), Spring Data offers **Specifications** and **Query by Example**, which build the
query from the filters actually given.
:::

:::step{type=recap title="What you can do now"}
You can now ask the database real questions, without writing SQL:

- A **derived query** is a repository method whose **name** is the query: `findBy` + fields + keywords like
  `And`, `Or`, `GreaterThan`, `Between`, `ContainingIgnoreCase`, `IsNull`, `OrderBy...Asc/Desc`.
- The return type chooses the shape: `List`, `Optional`, `boolean` (`existsBy`), `long` (`countBy`).
- Names are checked against the entity at **start-up**.
- Let the **database** filter and sort (`where`, `order by`), not Java after `findAll()`.
- Check with `existsBy...` and answer **409 Conflict** for duplicates; keep the unique constraint as the net.

:::photo{src="/lesson-images/spring/spring-20-notes.webp" alt="Sketchnote: Derived queries. Name a repository method, and Spring Data writes the query from the name. Flow: findByCategoryOrderByNameAsc, Spring Data reads the name, SQL with where and order by, only matching rows. Remember: the return type chooses the shape; a misspelled field stops the start-up; let the database filter and sort; a duplicate gets 409 Conflict and the constraint stays as the net." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 21: products are not alone. Orders contain items, items point to products: relationships, and the
most famous performance trap in JPA.
:::
