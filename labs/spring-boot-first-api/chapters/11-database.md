:::step{type=story title="Why this chapter"}
Until now the Shop API kept everything in Java lists, so every restart lost the data. Real applications
store data in a database. This chapter connects the Shop API to one with **JPA**, the standard Java way
to map objects to tables, so you work with Java objects and Hibernate writes the SQL.

:::mission
In the `11-database` folder: make `Product` a JPA entity, and let the database itself refuse duplicate SKUs.
:::
:::

:::step{type=concept title="JPA, Hibernate and Spring Data JPA"}
Three names you will meet together:

- **JPA** (Jakarta Persistence) is the standard: annotations such as `@Entity` and an API for saving and
  loading objects.
- **Hibernate** is the implementation Spring Boot uses. It turns entity operations into SQL.
- **Spring Data JPA** adds repositories: you declare an interface and Spring writes the implementation.

`spring-boot-starter-data-jpa` brings all three. This lab uses **H2**, a database that runs inside the
application, in memory; the same code works with PostgreSQL or MySQL by changing the connection settings.
:::

:::step{type=concept title="Entities"}
An **entity** is a class mapped to a table:

```java
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private int pricePaise;

    protected Product() {}   // JPA creates objects through this
}
```

- `@Entity`: this class is stored in a table (here `product`).
- `@Id`: the primary key. `@GeneratedValue(IDENTITY)`: the database assigns it on insert.
- Every other field becomes a column; `pricePaise` becomes `price_paise`.
- JPA needs a constructor with no arguments to build objects from rows.

:::diagram{name="orm-mapping"}
The class describes the table; each object is one row.
:::
:::

:::step{type=example title="Worked example: a repository and a save"}
```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {}

Customer c = repository.save(new Customer("Asha"));   // INSERT INTO customer ...
c.getId();                                           // 1, assigned by the database
repository.findById(1L);                             // SELECT ... WHERE id = 1
repository.findAll();                                // SELECT ... FROM customer
repository.count();                                  // SELECT COUNT(*) ...
```

1. `JpaRepository<Customer, Long>` is the entity type and its id type.
2. Spring Data creates the implementation at start-up; you never write the class.
3. `save` inserts a new entity (or updates an existing one) and returns it with its id.
:::

:::step{type=predict title="Guess first"}
:::question
A class is used in `JpaRepository<Product, Long>`, but `Product` has no `@Entity`. What happens?
:::
- [ ] Spring stores it in a default table
- [x] The application fails to start: Product is not a managed type
- [ ] Every query returns an empty list
:::explain
Spring Data can only work with entities. Start-up stops with "Not a managed type: class Product", which
is the error you will see in this chapter's starter.
:::
:::

:::step{type=try title="Start it, and read the error"}
```bash run
cd 11-database && mvn -q -o package -DskipTests && java -jar target/database.jar 2>&1 | grep -m3 -E "Not a managed|Caused by"
```

The application refuses to start until `Product` is an entity. `data.sql` will then insert three products
into the new table at start-up.
:::

:::step{type=task task=product_entity title="Warm-up: make Product an entity"}
In `11-database`, make `Product` a JPA entity: `@Entity` on the class, `@Id` and
`@GeneratedValue(strategy = GenerationType.IDENTITY)` on `id`, and a protected constructor with no arguments.

`GET /products` then returns the three products from `data.sql`, each with an id.
:::

:::step{type=concept title="Column rules belong in the database too"}
`@Column` describes a column's rules:

```java
@Column(nullable = false, unique = true, length = 40)
private String sku;
```

Hibernate creates the table with `NOT NULL` and a `UNIQUE` constraint. The database then refuses a
duplicate or a missing value, even if some code forgets to check, and Spring reports it as a
`DataIntegrityViolationException`. Validation in the API (chapter 8) gives good error messages;
database constraints make sure bad data can never be stored.
:::

:::step{type=task task=unique_sku title="One product per SKU"}
Make the database refuse a second product with the same `sku`, and a product with no `sku`, using
`@Column` on the `sku` field.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation marks the primary key of an entity?
:::
- [ ] `@Column(unique = true)`
- [x] `@Id`
- [ ] `@Entity`
:::explain
`@Id` marks the primary key; `@GeneratedValue` says who generates it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does Spring Data generate for `interface ProductRepository extends JpaRepository<Product, Long>`?
:::
- [ ] Nothing: you must implement the interface
- [x] An implementation with save, findById, findAll, delete, count and more
- [ ] A database table
:::explain
Spring Data creates the implementation at start-up. The table comes from the entity, created by
Hibernate here, and by migrations in chapter 16.
:::
:::

:::step{type=deep-dive title="Where the schema comes from"}
`spring.jpa.hibernate.ddl-auto=create-drop` lets Hibernate create the tables at start-up and drop them at
shutdown: convenient for learning and tests. Production never uses it: data would be lost and changes
are uncontrolled. Real projects keep `ddl-auto=validate` (check the tables match the entities) and create
tables with versioned migrations, which chapter 16 covers with Flyway.
:::

:::step{type=recap title="Chapter done"}
- JPA is the standard, Hibernate implements it, Spring Data JPA generates repositories.
- `@Entity` maps a class to a table; `@Id` and `@GeneratedValue` define the primary key.
- `JpaRepository<Entity, IdType>` gives save, find, delete and count without code.
- `@Column(nullable = false, unique = true)` adds database constraints that protect the data.
:::
