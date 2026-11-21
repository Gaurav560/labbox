:::step{type=story title="One app, many places"}
Your Shop API will not live on one computer. It runs on your laptop while you develop it, on a test
server where the team tries new features, and on the production server that real customers use. Same
code, different surroundings: a different database address on each, a different free-delivery threshold
for a festival sale, debug logs on your laptop but not in production.

If those values were written into the Java code, you would need a different build for every place. Instead,
Spring Boot keeps them **outside the code**, in configuration, and gives you a clean way to have
**different values in different places**.

In chapter 4 you read one setting with `@Value`. This chapter does configuration properly: settings files
in YAML, a typed Java class holding all of the shop's settings, where else settings can come from, and
**profiles** for production.

:::mission
Read the shop's settings into a typed `ShopProperties` record, and give production its own values with a
`prod` profile.
:::
:::

:::step{type=concept title="properties or YAML: two ways to write the same thing" file="07-configuration-and-profiles/src/main/resources/application.yml" line="1-3"}
So far you wrote settings in `application.properties`, one per line:

```properties
spring.application.name=shop-api
shop.name=Shop API
shop.free-delivery-above-paise=50000
```

This chapter's project uses `application.yml` instead (it has opened on the right). **YAML** writes the
same settings as a tree, using **indentation**:

```yaml
spring:
  application:
    name: shop-api
shop:
  name: Shop API
  free-delivery-above-paise: 50000
```

Read it as "`spring` contains `application`, which contains `name`". Each level of indentation (two
spaces) is one more dot in the properties version. Both files mean exactly the same to Spring; teams choose
whichever they find easier to read. YAML is nice when many settings share a prefix, because you write the
prefix once.

Two YAML rules that catch everyone at least once:

- **Spaces only, never tabs**, and the indentation must line up exactly.
- **A space after the colon**: `name: Shop API`, not `name:Shop API`.

Notice the naming style too: `free-delivery-above-paise`, lowercase words joined by dashes. That is called
**kebab-case**, and it is the recommended style for Spring settings.
:::

:::step{type=concept title="Many settings? Use a settings class"}
`@Value` is fine for one or two values. But the shop will have many settings: name, delivery threshold,
support email, opening hours, tax rate... Scattering `@Value("${shop....}")` across ten classes gets messy
fast: the same string repeated in many places, a typo in one of them, and no single place that shows all
the shop's settings.

The better way is a **settings class**: one Java type that holds every setting under one prefix. Spring
fills it at start-up, and any bean that needs settings simply injects it:

```java
@ConfigurationProperties(prefix = "delivery")
public record DeliveryProperties(String partner, int maxKm, Duration slot) { }
```

with these settings:

```yaml
delivery:
  partner: Dunzo
  max-km: 8
  slot: 30m
```

`@ConfigurationProperties(prefix = "delivery")` says: "fill this record from the settings under
`delivery`". Each component of the record is matched to a setting by name.

Look at the names closely: the setting is `max-km`, the record component is `maxKm`. Spring matches them
anyway. This is called **relaxed binding**: `max-km`, `maxKm`, `max_km` and `MAX_KM` all mean the same
setting. And look at `slot: 30m`: Spring even converts text into the right Java type, here a `Duration`
of 30 minutes. Numbers, booleans, durations, sizes like `10MB`, lists: all converted for you.
:::

:::step{type=example title="Worked example: using the settings class"}
Once the record exists, using it is just dependency injection, which you already know:

```java
@RestController
public class DeliveryController {

    private final DeliveryProperties delivery;

    public DeliveryController(DeliveryProperties delivery) {      // Spring passes the filled record
        this.delivery = delivery;
    }

    @GetMapping("/delivery/info")
    public Map<String, Object> info() {
        return Map.of("partner", delivery.partner(), "maxKm", delivery.maxKm());
    }
}
```

`GET /delivery/info` answers `{"partner":"Dunzo","maxKm":8}`.

One more thing makes it work: Spring must know the settings class exists. In this chapter's project,
`ShopApiApplication` already has **`@ConfigurationPropertiesScan`**, which tells Spring to look for
`@ConfigurationProperties` classes in the scanned packages, the same way component scanning finds
controllers.

`Map.of(...)` builds a small map of keys and values, which Jackson writes as a JSON object. It is a quick
way to answer with a few named values.
:::

:::step{type=task task=shop_properties title="Your turn: the shop's settings class"}
Three small changes, in three files:

1. **`application.yml`**: at the first TODO, add the shop's settings: under `shop`, a `name` of `Shop API`
   and a `free-delivery-above-paise` of `50000`.
2. **`config/ShopProperties.java`**: bind the record to the settings under the `shop` prefix.
3. **`config/ShopInfoController.java`**: receive `ShopProperties` in a constructor, and answer
   `GET /shop/info` with its `name` and `freeDeliveryAbovePaise`.

Build, run and try:

```bash run
cd 07-configuration-and-profiles && mvn -q -o package -DskipTests && java -jar target/configuration.jar
```

```bash run
curl localhost:8080/shop/info
```

You should see `{"name":"Shop API","freeDeliveryAbovePaise":50000}` (the two keys may come in either order).
Press **Check**.
:::

:::step{type=concept title="Where else settings come from"}
`application.yml` is not the only source of settings. Spring Boot reads settings from many places, and
when the same setting appears in more than one, **the more specific source wins**. The most important
sources, from weakest to strongest:

1. **`application.yml` / `application.properties`** inside the jar: the defaults you ship.
2. **`application-{profile}.yml`** for the active profile (next steps): overrides for one environment.
3. **Environment variables** of the process, like `SHOP_NAME=...`. (Relaxed binding again: `SHOP_NAME`
   means `shop.name`; dots and dashes become underscores, all in capitals.)
4. **Command-line arguments**: `java -jar app.jar --shop.name=...`.

This order is designed for how apps are run. The jar carries sensible defaults; each server sets what is
different through environment variables, which is how most hosting platforms (Docker, Kubernetes, cloud
services) pass configuration to an app; and a quick experiment can override anything on the command line.

Try the strongest one now (with your settings class working):

```bash run
java -jar target/configuration.jar --shop.name="Shop API (night test)"
```

and in the second terminal, `curl localhost:8080/shop/info`. The command line beat the file. Stop the app.
:::

:::step{type=concept title="Profiles: a set of settings for one environment"}
Production usually differs from development in *several* settings at once. You do not want to pass ten
command-line arguments every time. That is what **profiles** are for.

A profile is just a **name** for an environment, such as `dev`, `test` or `prod`. For each profile, you can
add a file named after it, next to `application.yml`:

```text
src/main/resources/
  application.yml          always read: the defaults
  application-prod.yml     read ONLY when the "prod" profile is active, on top of the defaults
```

The profile file only needs the settings that are **different**. Everything else still comes from
`application.yml`. If both files set `shop.name`, the profile's value wins.

You activate a profile when you start the app, in any of the ways settings can be given:

```bash
java -jar app.jar --spring.profiles.active=prod        # on the command line
SPRING_PROFILES_ACTIVE=prod java -jar app.jar          # or as an environment variable
```

And the start-up log tells you which profile is active. Remember this line from chapter 4?

```text
No active profile set, falling back to 1 default profile: "default"
```

With the prod profile, it says instead:

```text
The following 1 profile is active: "prod"
```

Always glance at that line when something behaves differently than you expect on a server.
:::

:::step{type=predict title="Guess first"}
:::question
`application.yml` sets `shop.name: Shop API`. `application-prod.yml` sets `shop.name: Shop API (production)`. You start the app with no profile. What is shop.name?
:::
- [x] Shop API
- [ ] Shop API (production)
- [ ] Start-up fails: two values for one setting
:::explain
`application-prod.yml` is only read when the `prod` profile is active. Without it, only `application.yml`
counts.
:::
:::

:::step{type=task task=prod_profile title="Your turn: production settings"}
In production, the shop shows a different name and only offers free delivery above Rs 1000.

Create a new file **`application-prod.yml`** in `src/main/resources/` (next to `application.yml`), with:

- `shop.name`: `Shop API (production)`
- `shop.free-delivery-above-paise`: `100000`

(In the editor's file tree, right-click the `resources` folder and choose **New File**; or in the terminal,
create it with any editor you like.) Write it as YAML, with `shop:` and the two settings indented under it.

Then rebuild and run with the profile:

```bash run
mvn -q -o package -DskipTests && java -jar target/configuration.jar --spring.profiles.active=prod
```

Check the start-up log for `The following 1 profile is active: "prod"`, then `curl localhost:8080/shop/info`.
You should see the production values. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which setting name matches the record component `freeDeliveryAbovePaise`?
:::
- [ ] Only free-delivery-above-paise
- [ ] Only freeDeliveryAbovePaise
- [x] Both, and also FREE_DELIVERY_ABOVE_PAISE as an environment variable
:::explain
Relaxed binding accepts all those forms. The recommended style in files is kebab-case,
`free-delivery-above-paise`; environment variables use capitals and underscores.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`application.yml` says port 8080, and the server starts with `--server.port=9090` on the command line. Which port?
:::
- [ ] 8080: the file is the source of truth
- [x] 9090: command-line arguments beat the settings file
- [ ] Start-up fails because of the conflict
:::explain
More specific sources win: command line over environment variables over profile files over
`application.yml`. That is what lets one jar run anywhere.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Where should the production database password go?
:::
- [ ] In application-prod.yml, committed with the code
- [x] In an environment variable (or a secrets manager) on the production server
- [ ] Hard-coded in a Java class
:::explain
Anything committed with the code can be read by everyone who can read the code, forever (git keeps
history). Secrets are passed to the running app from outside: environment variables, or a secrets store.
:::
:::

:::step{type=deep-dive title="Go deeper: validating settings, and config files outside the jar"}
**Validated settings.** Add `@Validated` to a settings record and constraints to its components
(`@NotBlank String name`, `@Min(0) int freeDeliveryAbovePaise`). A missing or wrong setting then stops the
app at start-up with a clear message, instead of failing at 2 a.m. on the first order. (Validation
annotations come in chapter 16.)

**Files outside the jar.** Spring Boot also reads `application.yml` from a `config/` folder next to the jar,
or from any path given with `--spring.config.location=...`. Operations teams use this to change settings
without rebuilding.

**Seeing every setting.** With the Actuator (chapter 2) and its `env` and `configprops` endpoints exposed,
you can see every setting and where its value came from. Very useful on a server; never expose them to the
public internet, because they can show secrets.
:::

:::step{type=recap title="What you can do now"}
You can now configure a Spring Boot app the way real teams do:

- Settings live outside the code, in `application.properties` or **YAML** (`application.yml`, indentation
  instead of dots, spaces only).
- A **settings class** with `@ConfigurationProperties(prefix = "...")` groups related settings in one typed
  record, found by `@ConfigurationPropertiesScan` and injected like any bean.
- **Relaxed binding**: `free-delivery-above-paise`, `freeDeliveryAbovePaise` and `FREE_DELIVERY_ABOVE_PAISE`
  are the same setting; text is converted to numbers, durations and more.
- Sources, weakest to strongest: settings file, profile file, environment variables, command line.
- **Profiles**: `application-prod.yml` overrides the defaults when started with
  `--spring.profiles.active=prod` (or `SPRING_PROFILES_ACTIVE=prod`); the log shows the active profile.
- Secrets never go into files committed with the code.

Next, chapter 8 answers a question you have had since chapter 0: how does Spring Boot decide what to
configure for you? You will build a small auto-configuration yourself.
:::
