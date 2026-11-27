:::step{type=story title="The database outlives the app"}
Until now, Hibernate created the tables every time the app started (`ddl-auto=create-drop`) and threw them
away when it stopped. Perfect for learning. Impossible in real life: the production database holds every
customer, every order, every product the shop has ever had. It lives for years, through hundreds of versions
of your app.

So how does the database change when the app changes? Version 12 of the Shop API adds a `category` to
products. The production database's `product` table has no such column, and it is full of real data that must
not be lost. Someone has to run `ALTER TABLE` (the SQL command that changes an existing table's structure), exactly once,
on every database (your laptop, the test server,
production), in the right order, and remember that it was done.

That someone is a **migration tool**. In this chapter you use the most common one in the Java world,
**Flyway**, and change a live schema the way professional teams do.

:::mission
Add a category column with a Flyway migration, then fill in the categories with a second one.
:::
:::

:::step{type=concept title="Migrations: the schema has a history, like your code"}
The idea is simple and powerful: every change to the database structure is a small **SQL script**, numbered in
order, stored **with your code**:

```text
src/main/resources/db/migration/
  V1__create_product.sql      the first version of the schema
  V2__add_category.sql        version 2: add a column
  V3__set_categories.sql      version 3: fill it in
```

At start-up, Flyway looks at the database and asks: "which of these scripts have already run here?" It runs
**only the new ones**, **in version order**, and records each one in a table it manages,
`flyway_schema_history`. Next start-up, nothing to do. On a brand new database, it runs all of them, from V1,
and ends up with exactly the same schema as everywhere else.

:::diagram{name="flyway-versions"}
Each file runs once, in version order, on every database.
:::

So the schema gets a history, just like your code in git: you can see every change, who made it (git blame on
the file), and every environment is guaranteed to have the same structure.
:::

:::step{type=concept title="The rules of a migration file"}
Flyway is strict about names, and for good reasons:

- **The name** is `V<version>__<description>.sql`: a capital **V**, the version number, **two** underscores,
  then a description with underscores for spaces. `V2__add_category.sql` is version 2, "add category".
  A single underscore, or a lower-case `v`, and Flyway ignores the file silently.
- **Never edit a migration that has run.** Flyway stores a **checksum** of each applied script (a number computed
  from the file's exact contents; change one character and the number changes). If you change
  `V1__create_product.sql` after it ran, the next start-up **fails** with a checksum mismatch: the file no longer
  describes what was actually done. To change something, you always add a **new** version.
- **Versions only go forward.** You fix a mistake in V2 with a V3, not by rewriting V2.

These rules feel strict at first. They are what makes it safe to run the same scripts, months apart, on
databases full of real data.
:::

:::step{type=concept title="Hibernate stops creating tables: ddl-auto=validate" file="24-migrations/src/main/resources/application.properties" line="1-4"}
With Flyway in charge of the schema, Hibernate must stop creating tables. Look at this project's settings, on the
right:

```properties
spring.jpa.hibernate.ddl-auto=validate
```

**`validate`** means: Hibernate does not create or change anything; it only **checks** at start-up that the
tables match the entities. If an entity has a field whose column is missing, the app refuses to start. That is a
safety check: you find out on deploy, not when the first customer opens a product page.

Adding Flyway to a Spring Boot project is one dependency, `org.flywaydb:flyway-core` (it is in this project's
pom). Spring Boot sees it and runs the migrations from `db/migration` automatically at start-up, before
Hibernate validates.

The project already has `V1__create_product.sql`, which creates the table and inserts three products (in real
life, data like that often comes from the app, but a migration can insert rows too).
:::

:::step{type=try title="The entity is ahead of the database" file="24-migrations/src/main/java/com/shop/product/Product.java" line="21"}
The `Product` entity, on the right, has a new field: `category`. Version 12 of the app wants it. The database
(made by V1) does not have that column. Start the app:

```bash run
cd 24-migrations && mvn -q -o package -DskipTests && java -jar target/migrations.jar
```

It refuses to start. Look for the cause (from our lab machine):

```text
Schema-validation: missing column [category] in table [product]
```

That is `validate` doing its job: the code and the database disagree, and it would be wrong to start. Look a
little higher in the log too, at Flyway's own lines:

```text
Successfully validated 1 migration (execution time 00:00.008s)
Migrating schema "PUBLIC" to version "1 - create product"
Successfully applied 1 migration to schema "PUBLIC", now at version v1 (execution time 00:00.014s)
```

(`PUBLIC` is H2's default **schema**: a named group of tables inside one database.)

Flyway ran V1. Now you need a V2.
:::

:::step{type=example title="Worked example: a migration that adds a column"}
Here is a migration that adds a `phone` column to an existing `customer` table full of real customers:

```sql
-- V7__add_customer_phone.sql
-- Customers gain a phone number. Existing customers have none yet.
ALTER TABLE customer ADD COLUMN phone VARCHAR(15);
```

And one that adds a **required** column. Existing rows need *some* value, or the `NOT NULL` rule would be broken
the moment the column appears, so you give a **default**:

```sql
-- V8__add_customer_tier.sql
ALTER TABLE customer ADD COLUMN tier VARCHAR(20) DEFAULT 'regular' NOT NULL;
```

Every existing customer gets `regular`; new ones can be given anything. A comment at the top, saying *why*, is a
gift to whoever reads the history next year.
:::

:::step{type=task task=add_category_column title="Your turn: V2 adds the category column"}
Create **`src/main/resources/db/migration/V2__add_category.sql`** (next to V1) that adds to `product` a column
**`category`**: `VARCHAR(40)`, **not null**, with the **default** `'other'`.

Mind the name: capital `V`, `2`, **two underscores**. Then rebuild and run. Flyway's lines now say:

```text
Migrating schema "PUBLIC" to version "1 - create product"
Migrating schema "PUBLIC" to version "2 - add category"
Successfully applied 2 migrations to schema "PUBLIC", now at version v2
```

(Flyway runs V1 again because this lab's H2 database lives in memory and starts empty each time. On a real
database it would run only V2.) And the app starts. `curl localhost:8080/products` shows every product with `"category":"other"`. Press **Check**.

Usual slips: one underscore (`V2_add_category.sql`; see the second quick check below), or renaming a migration file
and rebuilding with `mvn package` only. `package` does not delete old files from `target/`, so the old name is still
there and Flyway sees both. We fell into exactly this on our lab machine; after renaming a migration, build with
`mvn -q -o clean package -DskipTests` (`clean` empties `target/` first).
:::

:::step{type=concept title="Data migrations"}
A migration does not have to change the structure. It can change **data** too. Now that every product has
the category `other`, someone has to sort them: the kulfis and custards are sweets, the samosa is a snack.

That is also a migration, with the next version number, so it runs exactly once on every database, after the
column exists:

```sql
-- V9__tier_for_big_spenders.sql
UPDATE customer SET tier = 'gold' WHERE total_spent_paise > 5000000;
```

Why not run that `UPDATE` by hand on production? Because then the test server, every developer's laptop and the
next new environment would *not* have it. Anything the database needs, it gets through a migration.
:::

:::step{type=task task=set_categories title="Your turn: V3 sets the categories"}
Create **`V3__set_categories.sql`**: the two sweets, **KUL-1** and **CUS-1**, get the category **`sweets`**,
and **SAM-1** gets **`snacks`**. (Use `UPDATE ... SET ... WHERE sku ...`; `WHERE sku IN ('A', 'B')` matches
several values.)

Rebuild and run: Flyway now migrates to version 3, and `curl localhost:8080/products` shows the right categories.
On our lab machine:

```text
[{"id":1,"name":"Mango kulfi",...,"category":"sweets","sku":"KUL-1"},{"id":2,"name":"Fruit custard",...,"category":"sweets","sku":"CUS-1"},{"id":3,"name":"Samosa",...,"category":"snacks","sku":"SAM-1"}]
```

Press **Check**.

Usual slips: double quotes around the values (`"sweets"`; SQL text values use single quotes: `'sweets'`), or
editing V2 to set the categories instead of adding V3.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
You notice a typo in V2__add_category.sql, which has already run on production. What do you do?
:::
- [ ] Edit V2 and restart
- [x] Leave V2 as it is, and add V4 that fixes it
- [ ] Delete the flyway_schema_history table
:::explain
Editing an applied migration breaks its checksum, and the next start-up fails. History only moves forward: a
new version fixes it, on every database.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A file is named `V4_add_index.sql` (one underscore). What happens?
:::
- [ ] Flyway runs it as version 4
- [x] Flyway does not recognise it as a migration, and silently skips it
- [ ] Start-up fails
:::explain
The separator is two underscores. With one, the name does not match Flyway's pattern, and the file is ignored
without a word. We tried it on our lab machine with V2 named `V2_add_category.sql`: Flyway said "Successfully
validated 2 migrations", ran V1, skipped V2, and then V3 failed, because the column V2 should have added was not
there. One of the most common migration mistakes.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
With `ddl-auto=validate`, an entity has a column the table lacks. What happens?
:::
- [ ] Hibernate adds the column
- [x] The app refuses to start: schema validation fails
- [ ] The field is always null
:::explain
`validate` only checks. It never changes the schema; that is Flyway's job. A mismatch stops the start-up, so it is
found on deploy, not by a customer.
:::
:::

:::step{type=deep-dive title="Go deeper: production migrations"}
**Big tables.** On a table with millions of rows, some `ALTER TABLE`s lock it for minutes. Teams then split a
change into small, safe steps across several releases (add a nullable column, backfill in batches, then add the
constraint).

**Backward compatible changes.** While a new version is being deployed, old and new copies of the app run side by
side against the same database. So a migration must not break the old version: add before you remove, rename in
two steps (add the new column, copy, switch the code, drop the old one later).

**Liquibase** is the other common migration tool, with changes described in XML, YAML or SQL. The ideas are the
same.

**Undo.** Flyway's free edition has no automatic "down" migrations, on purpose: in production you fix forward with
a new version, which is tested like any other change.
:::

:::step{type=recap title="What you can do now"}
You can now change a database that holds real data, safely:

- A **migration tool** (Flyway) runs numbered SQL scripts from `db/migration` in version order, **once each**, and
  records them in `flyway_schema_history`. Every environment ends up identical.
- Names: **`V<version>__<description>.sql`** (capital V, two underscores). Never edit an applied migration; fix
  forward with a new version.
- **`ddl-auto=validate`**: Hibernate only checks that tables match entities; Flyway owns the schema.
- New required columns need a **default** for existing rows; **data** changes are migrations too.

:::photo{src="/lesson-images/spring/spring-24-notes.webp" alt="Sketchnote: Migrations with Flyway. Every database change is a numbered SQL file, run once, in order, on every database. Flow: V1, V2, V3, recorded in flyway_schema_history. Remember: the name is V, the version, two underscores, a description; never edit an applied migration; ddl-auto=validate only checks; a new required column on a table with rows needs a default." ai="true"}
One page of notes for this chapter.
:::

That completes Part 3: the Shop API has a real, evolving database. Part 4 makes it production-ready, starting
with chapter 25: writing your own tests.
:::
