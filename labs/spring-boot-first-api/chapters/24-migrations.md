:::step{type=story title="Why this chapter"}
So far Hibernate created the tables from the entities at every start. That cannot work in production:
the database already holds data, and its structure must change in controlled steps that every
environment applies the same way. This chapter manages the schema with **Flyway**, versioned SQL files
that run once each, in order.

:::mission
In the `24-migrations` folder: add a column with a migration, then fill it with a second one.
:::
:::

:::step{type=concept title="Versioned migrations"}
A **migration** is a SQL file that changes the schema, named with a version:

```text
src/main/resources/db/migration/
  V1__create_product.sql
  V2__add_category.sql
```

At start-up, Flyway compares these files with the table `flyway_schema_history` in the database, runs the
ones not applied yet **in version order**, and records each one. Every database (your laptop, the test
server, production) reaches the same schema the same way.

Files are never edited once applied: Flyway stores a checksum and refuses to start if an applied file
changed. To change the schema again, add a new version.

:::diagram{name="flyway-versions"}
Each file runs once, in order, and is recorded in the history table.
:::
:::

:::step{type=concept title="Hibernate validates, Flyway changes"}
With Flyway, Hibernate no longer creates tables:

```properties
spring.jpa.hibernate.ddl-auto=validate
```

At start-up Hibernate only **checks** that the tables match the entities. If an entity has a field the table
does not, start-up fails with "missing column". The fix is always a new migration, never a change to an
old one.
:::

:::step{type=example title="Worked example: adding a column to a table with data"}
```sql
-- V4__add_discount.sql
ALTER TABLE product ADD COLUMN discount_percent INT DEFAULT 0 NOT NULL;
```

1. `ALTER TABLE ... ADD COLUMN` changes the existing table; existing rows stay.
2. `DEFAULT 0 NOT NULL`: existing rows need a value for a `NOT NULL` column, so the default fills them.
3. The entity gets `private int discountPercent;`, and `validate` confirms they match.
:::

:::step{type=predict title="Guess first"}
:::question
`V2__add_category.sql` was applied yesterday. Today you edit it to rename the column. What happens at the next start?
:::
- [ ] Flyway runs the new version of the file
- [x] Flyway refuses to start: the applied file's checksum changed
- [ ] Nothing: the file is ignored
:::explain
Applied migrations are history. Flyway detects the change and stops. Rename the column in a new
migration, `V3__rename_category.sql`.
:::
:::

:::step{type=try title="See it refuse to start"}
```bash run
cd 24-migrations && mvn -q -o package -DskipTests && java -jar target/migrations.jar 2>&1 | grep -m2 -E "missing column|Started"
```

The entity has `category`, the table does not: `validate` stops the application.
:::

:::step{type=task task=add_category_column title="Warm-up: a migration that adds a column"}
In `24-migrations/src/main/resources/db/migration/`, add `V2__add_category.sql` that adds the column
`category` to `product`: `VARCHAR(40)`, `NOT NULL`, `DEFAULT 'other'`.

The application starts, and `GET /products` shows a category for each product.
:::

:::step{type=task task=set_categories title="A data migration"}
Migrations can change data too. Add `V3__set_categories.sql`: the products with SKU `TEA-1` and `COF-1` get
the category `drinks`, and `SAM-1` gets `snacks`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
In which order does Flyway run `V2__a.sql`, `V10__b.sql` and `V3__c.sql`?
:::
- [ ] Alphabetical: V10, V2, V3
- [x] By version number: V2, V3, V10
- [ ] By file date
:::explain
Flyway compares versions as numbers, so 10 comes after 3.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where does Flyway record which migrations a database has applied?
:::
- [ ] In `application.properties`
- [x] In the table `flyway_schema_history`, inside that database
- [ ] In a file on the server
:::explain
Each database keeps its own history, so every environment knows exactly what it still needs.
:::
:::

:::step{type=deep-dive title="Migrations in a team"}
Two developers creating `V5` on different branches will clash at merge time, so teams agree on numbering,
or use timestamps as versions (`V20261121_1200__...`). Make large changes in safe steps: add a new
column, copy data, switch the code, and only later drop the old column, so the running version of the
application keeps working during a deployment. Liquibase is the main alternative to Flyway, with the same
idea in XML, YAML or SQL.
:::

:::step{type=recap title="Chapter done"}
- Flyway runs versioned SQL files once each, in version order, and records them in `flyway_schema_history`.
- With `ddl-auto=validate`, Hibernate checks the schema; migrations change it.
- Never edit an applied migration: add a new version.
- Migrations can change data as well as structure.
:::
