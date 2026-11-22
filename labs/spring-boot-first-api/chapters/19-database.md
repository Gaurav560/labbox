:::step{type=story title="Part 3: data that survives"}
Welcome to Part 3. Until now, every product the Shop API knew lived in a Java list, in memory. Stop the app,
and every product a shopkeeper added is gone. Start two copies of the app (as real servers do, to handle
more customers), and each has its own different list. That is fine for learning HTTP. It is not a shop.

Real applications keep their data in a **database**: a separate program built to store data safely, share it
between many app instances, survive restarts and crashes, and find things fast. In this part you will
connect the Shop API to one, and learn the tools Spring gives you for it: **JPA**, **Hibernate** and
**Spring Data**.

This first chapter goes slowly, because there are several new ideas at once. By the end, products will be
rows in a real database table, created from your Java class.

:::mission
Turn `Product` into a JPA entity stored in a database table, and let the database refuse duplicate SKUs.
:::
:::

:::step{type=concept title="Databases in five minutes"}
The databases most backends use are **relational databases**: PostgreSQL, MySQL, Oracle, SQL Server, and the
small one we use in this lab, **H2**. They all store data the same way: in **tables**.

```text
table: product
+----+---------------+-------------+-------+
| id | name          | price_paise | sku   |
+----+---------------+-------------+-------+
|  1 | Mango lassi    |        2000 | LAS-1 |
|  2 | Filter coffee |        3000 | COF-1 |
|  3 | Samosa        |        1800 | SAM-1 |
+----+---------------+-------------+-------+
```

- A **table** holds one kind of thing (products).
- Each **row** is one thing (one product).
- Each **column** is one property, with a fixed type (text, number, date...).
- The **primary key** (`id`) uniquely identifies each row. No two rows share one.

You talk to a relational database in **SQL**, a language of short commands:

```sql
SELECT name, price_paise FROM product WHERE price_paise < 2500;   -- read rows
INSERT INTO product (name, price_paise, sku) VALUES ('Poha', 2200, 'POH-1');   -- add a row
UPDATE product SET price_paise = 2100 WHERE id = 1;                -- change rows
DELETE FROM product WHERE id = 3;                                  -- remove rows
```

(If SQL is new to you, the *SQL from zero* course in LabBox teaches it properly. For this chapter, reading
these four lines is enough.)

**H2** is a database written in Java that can run *inside* your app, in memory. It is perfect for learning
and for tests: nothing to install. In production you would point the same code at PostgreSQL or MySQL by
changing a setting.
:::

:::step{type=concept title="From objects to rows: ORM, JPA and Hibernate"}
Your Java code thinks in **objects** (`new Product("Lassi", 2000, "LAS-1")`); the database thinks in **rows**.
Writing SQL by hand to convert between them for every class is long, repetitive work. The tool that does it
for you is called an **ORM**, an Object-Relational Mapper.

:::diagram{name="orm-mapping"}
One class maps to one table, each field to a column, each object to a row.
:::

Three names you will see constantly, and how they relate:

- **JPA** (Jakarta Persistence API) is the **standard**: a set of annotations (`@Entity`, `@Id`...) and
  rules for mapping Java classes to tables. It is only a specification, like a contract.
- **Hibernate** is the **implementation**: the library that actually reads your annotations, writes the SQL
  and runs it. It is by far the most used JPA implementation, and the one Spring Boot uses.
- **Spring Data JPA** sits on top: it writes your **repositories** for you (you will see how in a minute).

All three come in with one starter: **`spring-boot-starter-data-jpa`**. This chapter's `pom.xml` has it,
plus the `h2` database driver.
:::

:::step{type=concept title="How the app reaches the database" file="19-database/src/main/resources/application.properties" line="1-5"}
`application.properties` has opened on the right. The database settings:

```properties
spring.datasource.url=jdbc:h2:mem:shop;DB_CLOSE_DELAY=-1
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.defer-datasource-initialization=true
```

- **`spring.datasource.url`** says *which* database. It is a **JDBC URL**: JDBC is Java's standard way to
  talk to any database, and every database has its URL format. `jdbc:h2:mem:shop` means "an H2 database, in
  memory, named shop". For PostgreSQL it would look like `jdbc:postgresql://db-server:5432/shop`.
- **`spring.jpa.hibernate.ddl-auto=create-drop`** tells Hibernate to **create the tables from your entity
  classes** at start-up, and drop them at shutdown. Handy for learning. Never in production, where tables
  hold real data; chapter 24 shows the proper way, with migration scripts.
- **`defer-datasource-initialization`** makes Spring run `data.sql` (the three `INSERT`s in this project)
  *after* Hibernate created the tables, so the shop starts with three products.

Opening a database connection is slow, so Spring Boot keeps a small set of them open and reuses them: a
**connection pool**, called **HikariCP**. You will see it in the start-up log:

```text
HikariPool-1 - Starting...
HikariPool-1 - Added connection conn0: url=jdbc:h2:mem:shop user=SA
HikariPool-1 - Start completed.
```
:::

:::step{type=concept title="Spring Data writes your repository" file="19-database/src/main/java/com/shop/product/ProductRepository.java" line="5-7"}
`ProductRepository` is on the right, and it is surprisingly short:

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
}
```

It is an **interface** with no methods of its own, and there is **no class implementing it**. Yet
`ProductController` calls `repository.findAll()`, and it works. How?

At start-up, **Spring Data** sees every interface that extends `JpaRepository` and **generates a class for
it**, with dozens of ready methods, then registers it as a bean:

- `findAll()`, `findById(id)`, `count()`, `existsById(id)`
- `save(entity)` (insert or update), `saveAll(list)`
- `deleteById(id)`, `delete(entity)`

The two types in the angle brackets say **which entity** (`Product`) and **the type of its id** (`Long`).

Remember the hand-written in-memory repositories in Part 2, with `findById` written using streams? You will
never write those again. In chapter 20 you will even get custom queries generated from method names.
:::

:::step{type=try title="The app refuses to start" file="19-database/src/main/java/com/shop/product/Product.java" line="3-15"}
Now the class being stored: `Product.java`, on the right. It is a plain class with fields, a constructor and
getters. Run the app:

```bash run
cd 19-database && mvn -q -o package -DskipTests && java -jar target/database.jar
```

It stops at start-up. Among the error lines:

```text
Not a managed type: class com.shop.product.Product
```

Spring Data tried to build a repository for `Product`, but JPA does not know `Product`. It is just a class,
not something JPA manages. To JPA, a class is only storable if it is marked as an **entity**.
:::

:::step{type=concept title="Making an entity"}
An **entity** is a class whose objects JPA stores as rows. Here is a customer entity, piece by piece:

```java
@Entity
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    private String email;

    protected Customer() {        // for JPA only
    }

    public Customer(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // getters...
}
```

- **`@Entity`**: "store objects of this class in a table". The table name comes from the class: `customer`.
- **`@Id`**: this field is the **primary key**.
- **`@GeneratedValue(strategy = GenerationType.IDENTITY)`**: the **database** chooses the id when the row
  is inserted (1, 2, 3...). That is why the constructor does not take an id, and why it is a `Long` (an
  object, which can be `null` before saving) rather than a `long`.
- Every other field becomes a **column**: `name`, `email`. Java's `camelCase` names become
  `snake_case` columns: `pricePaise` becomes `price_paise`.
- **A constructor with no arguments.** When Hibernate *reads* a row, it first creates an empty object, then
  fills the fields. It needs a no-argument constructor for that. Making it `protected` lets Hibernate use it
  while your own code keeps using the real constructor.

The annotations come from `jakarta.persistence`.
:::

:::step{type=task task=product_entity title="Your turn: make Product an entity"}
In `Product.java`:

1. Mark the class as an entity.
2. Mark `id` as the primary key, with its value generated by the database (`IDENTITY`).
3. Add a `protected` constructor with no arguments.

Rebuild and run. This time the app starts, and:

```bash run
curl localhost:8080/products
```

```text
[{"id":1,"name":"Mango lassi","pricePaise":2000,"sku":"LAS-1"},{"id":2,"name":"Filter coffee","pricePaise":3000,"sku":"COF-1"},{"id":3,"name":"Samosa","pricePaise":1800,"sku":"SAM-1"}]
```

Those three products came from `data.sql`, through a real database table. Press **Check**.
:::

:::step{type=example title="Watch the SQL Hibernate writes"}
Hibernate writes all the SQL for you, but you should always be able to *see* it. Run the app with SQL
logging switched on:

```bash run
java -jar target/database.jar --spring.jpa.show-sql=true
```

At start-up, Hibernate creates the table from your class:

```text
Hibernate: drop table if exists product cascade
Hibernate: create table product (price_paise integer not null, id bigint generated by default as identity, name varchar(255), sku varchar(255), primary key (id))
```

Compare it with `Product.java`: `id` became a `bigint` primary key generated by the database; `pricePaise`
became `price_paise integer not null` (an `int` can never be null, so the column cannot be either); `name`
and `sku` became text columns. Then, when you `curl localhost:8080/products`:

```text
Hibernate: select p1_0.id,p1_0.name,p1_0.price_paise,p1_0.sku from product p1_0
```

That is what `findAll()` turned into. Making a habit of reading this SQL is one of the best things you can do
as a Spring developer: chapter 21 shows how a single innocent-looking line can produce hundreds of queries,
and this log is how you catch it. Stop the app.
:::

:::step{type=concept title="Rules the database enforces: @Column"}
Look at the `sku` column in that `create table`: `sku varchar(255)`. Nothing stops two products from having
the same SKU, or none at all. A SKU (stock-keeping unit) is the shop's own product code, and it **must** be
unique: the warehouse, the barcode labels and the suppliers all rely on it.

You could check for duplicates in Java before saving. You should (chapter 20 does). But Java checks can be
skipped: another service writing to the same database, a bug, a script run by hand, two requests at the same
instant. The final safety net is the **database itself**, with a **constraint**.

**`@Column`** on a field describes its column, including constraints:

```java
@Column(nullable = false, unique = true)
private String email;
```

- `nullable = false` becomes `not null`: the database refuses a row without an email.
- `unique = true` becomes a `unique` constraint: the database refuses a second row with the same email.

If a save breaks a constraint, the database refuses it, and Spring turns the error into a
**`DataIntegrityViolationException`**. Nothing is stored.
:::

:::step{type=task task=unique_sku title="Your turn: one product per SKU"}
In `Product.java`, make the `sku` column **required** and **unique**.

Rebuild and run with `--spring.jpa.show-sql=true` again, and look at the new table definition:

```text
create table product (..., sku varchar(255) not null unique, primary key (id))
```

The check saves a second product with `LAS-1`, and one with no SKU, and expects the database to refuse both.
Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why does the entity's id use `Long` and not `long`?
:::
- [ ] JPA cannot store primitive types
- [x] Before saving, the database has not chosen an id yet, and a Long can be null to say so
- [ ] Long is faster
:::explain
With `GenerationType.IDENTITY`, the id exists only after the insert. `null` honestly means "not saved yet".
A `long` would be 0, which looks like a real id.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does Spring Data generate for `interface OrderRepository extends JpaRepository<Order, Long>`?
:::
- [ ] Nothing: you must write a class that implements it
- [x] A class with findAll, findById, save, delete, count and more, registered as a bean
- [ ] Only findAll
:::explain
Spring Data writes the implementation at start-up. You declare the interface; you get a full repository.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why also enforce uniqueness in the database, if the Java code already checks for duplicates?
:::
- [ ] Databases are faster at checking
- [x] Java checks can be bypassed (other code, scripts, two requests at the same instant); the constraint never is
- [ ] JPA requires it
:::explain
Two requests can both check "no LAS-1 yet" at the same moment, and both save. Only the database sees every
write, one at a time, so its constraint is the real guarantee.
:::
:::

:::step{type=deep-dive title="Go deeper: the H2 console, real databases, and ddl-auto values"}
**The H2 console.** H2 has a small web page for browsing the database. With `spring.h2.console.enabled=true`,
it is at `/h2-console` (use the JDBC URL from the settings to connect). Never enable it on a public server.

**Real databases.** To use PostgreSQL, you add its driver dependency (`org.postgresql:postgresql`) instead of
H2, and set `spring.datasource.url`, `username` and `password` (from environment variables, chapter 7). The
entities and repositories do not change. A tool called **Testcontainers** can start a real PostgreSQL in
Docker for your tests.

**ddl-auto.** `create-drop` (create, drop at shutdown), `create` (create, keep), `update` (try to alter tables
to match the classes: tempting, risky), `validate` (only check that tables match the classes: what you want
in production, together with migrations), `none`. Chapter 24 uses `validate`.
:::

:::step{type=recap title="What you can do now"}
The Shop API now stores its products in a real database:

- Relational databases store **rows** in **tables** with typed **columns** and a **primary key**, and speak
  **SQL**. **H2** runs in memory inside the app.
- **JPA** is the standard, **Hibernate** implements it (an **ORM**), **Spring Data JPA** writes repositories;
  all from `spring-boot-starter-data-jpa`.
- `spring.datasource.url` is a **JDBC URL**; **HikariCP** keeps a pool of connections.
- An **entity**: `@Entity`, `@Id` + `@GeneratedValue(strategy = GenerationType.IDENTITY)`, a protected no-argument
  constructor; fields become `snake_case` columns.
- **`JpaRepository<Entity, IdType>`**: an interface, implemented for you at start-up.
- **`@Column(nullable = false, unique = true)`** becomes database constraints; violations throw
  `DataIntegrityViolationException`.
- **`--spring.jpa.show-sql=true`** shows every query Hibernate runs. Read it.

Next, chapter 20: asking the database real questions, with queries Spring Data writes from method names.
:::
