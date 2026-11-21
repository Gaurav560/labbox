:::step{type=story title="Why this chapter"}
The same application runs on a laptop, a test server and production, with different database URLs,
limits and names. Those values must not be in the code. This chapter reads settings into typed Java
objects, and switches whole sets of them with profiles.

:::mission
In the `10-configuration` folder: read the shop's settings into a typed record, and add production
settings with a profile.
:::
:::

:::step{type=concept title="application.yml"}
Spring Boot reads `application.properties` or `application.yml`; both hold the same settings. YAML groups
them by indentation:

```yaml
shop:
  name: Shop API
  free-delivery-above-paise: 50000
```

is the same as `shop.name=Shop API` and `shop.free-delivery-above-paise=50000`. Indentation uses spaces,
never tabs. Settings can also come from environment variables: `SHOP_NAME=...` sets `shop.name`, which
is how production servers usually pass secrets and URLs.
:::

:::step{type=concept title="@ConfigurationProperties"}
`@Value` reads one property at a time. For a group of settings, bind them all to a record:

```java
@ConfigurationProperties(prefix = "shop")
public record ShopProperties(String name, int freeDeliveryAbovePaise) {}
```

With `@ConfigurationPropertiesScan` on the main class, Spring creates a `ShopProperties` bean filled from
every `shop.*` setting, and you inject it like any bean.

**Relaxed binding** matches names across styles: `free-delivery-above-paise` in YAML,
`freeDeliveryAbovePaise` in Java, `SHOP_FREEDELIVERYABOVEPAISE` as an environment variable. Values are
converted to the field's type, and a wrong type stops start-up with a clear error.
:::

:::step{type=example title="Worked example: delivery settings"}
```yaml
delivery:
  base-fee-paise: 3000
  max-distance-km: 12
```

```java
@ConfigurationProperties(prefix = "delivery")
public record DeliveryProperties(int baseFeePaise, int maxDistanceKm) {}

@Service
public class DeliveryService {
    private final DeliveryProperties settings;

    public DeliveryService(DeliveryProperties settings) {
        this.settings = settings;
    }

    public boolean canDeliver(int km) {
        return km <= settings.maxDistanceKm();
    }
}
```

Changing the limit to 15 km is now a one-line change in YAML, with no code change and no rebuild of the rules.
:::

:::step{type=predict title="Guess first"}
:::question
`application.yml` has `shop.free-delivery-above-paise: 50000`. The record field is `freeDeliveryAbovePaise`. Does it bind?
:::
- [x] Yes: relaxed binding matches the kebab-case name to the camelCase field
- [ ] No: the names must match exactly
- [ ] Only if the field is a `String`
:::explain
Spring Boot's relaxed binding treats `free-delivery-above-paise`, `freeDeliveryAbovePaise` and
`FREE_DELIVERY_ABOVE_PAISE` as the same property. Kebab-case is the recommended style in files.
:::
:::

:::step{type=try title="See the settings"}
```bash run
cd 10-configuration && mvn -q -o package -DskipTests && java -jar target/configuration.jar
```

In a second tab, after the first task:

```bash run
curl -s localhost:8080/shop/info; echo
```
:::

:::step{type=task task=shop_properties title="Warm-up: typed shop settings"}
In `10-configuration`: put `@ConfigurationProperties(prefix = "shop")` on `ShopProperties`, add the
`shop` settings to `application.yml` (name `Shop API`, free delivery above `50000` paise), and make
`ShopInfoController` receive `ShopProperties` in its constructor and answer with its values.
:::

:::step{type=concept title="Profiles"}
A **profile** is a named set of settings, such as `dev`, `test` or `prod`. Spring Boot reads
`application.yml` first, then `application-<profile>.yml` for each active profile. **Later values win**,
so a profile file only needs the settings that differ.

Activate a profile with `spring.profiles.active=prod`, the environment variable
`SPRING_PROFILES_ACTIVE=prod`, or on the command line: `java -jar app.jar --spring.profiles.active=prod`.

:::diagram{name="profile-layers"}
The profile file is applied on top of the base file; the values it sets win.
:::
:::

:::step{type=task task=prod_profile title="Production settings in a profile"}
Create `10-configuration/src/main/resources/application-prod.yml` that sets `shop.name` to
`Shop API (production)` and `shop.free-delivery-above-paise` to `100000`.

With the `prod` profile active, `GET /shop/info` shows those values; without it, the base values.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`application.yml` sets `shop.name: Shop API`; `application-prod.yml` does not mention `shop.name`. With `prod` active, what is the name?
:::
- [x] `Shop API`, from the base file
- [ ] `null`
- [ ] Start-up fails
:::explain
The profile file only overrides what it sets. Everything else comes from the base file.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where should a production database password come from?
:::
- [ ] Hard-coded in a Java class
- [ ] `application-prod.yml`, committed to Git
- [x] An environment variable or a secret store, read at start-up
:::explain
Secrets must not be in code or in the repository. Environment variables (or a secret manager) inject
them at run time, and relaxed binding maps them to properties.
:::
:::

:::step{type=deep-dive title="Where settings can come from, and in what order"}
Spring Boot combines many sources, and later ones override earlier ones. In short, from lowest to
highest: defaults in code, `application.yml`, profile files, environment variables, command-line arguments.
So `--server.port=9090` on the command line beats everything in files. Add
`@Validated` and constraints (`@Positive`) to a `@ConfigurationProperties` record to make the application
refuse to start with invalid settings.
:::

:::step{type=recap title="Chapter done"}
- `application.yml` holds settings; environment variables and command-line arguments can override them.
- `@ConfigurationProperties(prefix = "...")` binds a group of settings to a typed record; relaxed binding matches name styles.
- A profile adds `application-<profile>.yml` on top of the base file; its values win.
:::
