:::step{type=story title="Why this chapter"}
Anyone who can reach the Shop API can read the sales report or delete products. A real API must know
**who** is calling (authentication) and **what** they may do (authorization). Spring Security does both,
with a chain of filters that every request passes before it reaches a controller.

:::mission
In the `28-security` folder: keep the product list public, require a login for everything else, and let
only admins delete products.
:::
:::

:::step{type=concept title="Authentication and authorization"}
Two separate questions, with two separate status codes:

- **Authentication**: who are you? No login, or a wrong password, answers **401 Unauthorized**.
- **Authorization**: you are logged in, but may you do this? A logged-in user without the right role gets
  **403 Forbidden**.

Here users log in with **HTTP Basic**: the client sends `Authorization: Basic <base64 of user:password>`
with every request. It is simple and fine over HTTPS for internal tools; public APIs usually use tokens
(OAuth2, JWT), which plug into the same filter chain.
:::

:::step{type=concept title="The security filter chain"}
Add `spring-boot-starter-security` and every endpoint is locked at once, with a generated password printed
at start-up. You then describe the rules in a `SecurityFilterChain` bean:

:::diagram{name="security-chain"}
Every request passes the filters first; only allowed requests reach the controller.
:::

Rules are checked **top to bottom**, and the first one that matches decides. So put specific rules first
and `anyRequest()` last.
:::

:::step{type=example title="Worked example: a library API"}
```java
@Configuration
public class LibrarySecurity {

    @Bean
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        return http
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.GET, "/books/**").permitAll()
                        .requestMatchers("/librarian/**").hasRole("LIBRARIAN")
                        .anyRequest().authenticated())
                .httpBasic(Customizer.withDefaults())
                .build();
    }

    @Bean
    InMemoryUserDetailsManager users() {
        return new InMemoryUserDetailsManager(
                User.withUsername("meera").password("{noop}books1").roles("LIBRARIAN").build());
    }
}
```

`{noop}` means "this password is stored as plain text". It is only for labs and tests; real users are
stored with `{bcrypt}` hashes in a database.

:::trace{title="Who gets in"}
| request | user | first rule that matches | answer |
|---|---|---|---|
| GET /books/7 | nobody | GET /books/** permitAll | 200 |
| GET /librarian/loans | nobody | /librarian/** hasRole | 401 |
| GET /librarian/loans | ravi (READER) | /librarian/** hasRole | 403 |
| GET /librarian/loans | meera (LIBRARIAN) | /librarian/** hasRole | 200 |
:::
:::

:::step{type=concept title="CSRF, and why this API turns it off"}
**CSRF** (cross-site request forgery) protection stops another website from making a logged-in browser
send a request with its cookies. Spring Security turns it on by default, and then every `POST`, `PUT`
and `DELETE` needs a CSRF token, or it answers 403.

This API does not use browser cookies: every client sends its credentials with each request. CSRF does
not apply, so you turn it off with `.csrf(csrf -> csrf.disable())`. Keep it on for apps with browser
sessions and forms.
:::

:::step{type=predict title="Guess first"}
:::question
The rules are `.anyRequest().authenticated()` first, then `.requestMatchers(GET, "/products").permitAll()`. What does an anonymous GET /products get?
:::
- [ ] 200: the permitAll rule allows it
- [x] It never works: Spring refuses to start, because nothing can come after anyRequest()
- [ ] 403
:::explain
The first matching rule decides, and `anyRequest()` matches everything, so a rule after it could never
apply. Spring Security rejects that order at start-up.
:::
:::

:::step{type=try title="Knock on the doors"}
```bash run
cd 28-security && mvn -q -o package -DskipTests && java -jar target/security.jar
```

In a second tab:

```bash run
curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/products; curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/admin/report; curl -s -u staff:staff123 localhost:8080/admin/report; echo
```
:::

:::step{type=task task=public_and_protected title="Public list, protected rest"}
In `28-security/.../SecurityConfig.java`, define a `SecurityFilterChain` bean: `GET /products` open to
everyone, everything else needs a login with HTTP Basic, CSRF off. Define two users in memory:
`staff` / `staff123` with role `STAFF`, and `admin` / `admin123` with role `ADMIN`.
:::

:::step{type=task task=admin_only title="Only admins delete"}
Add a rule so that only `ADMIN` may `DELETE /products/{id}`. A logged-in `STAFF` user gets 403. Remember
that the order of the rules matters.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A request has the right username and the wrong password. Which status?
:::
- [x] 401
- [ ] 403
- [ ] 400
:::explain
The caller could not be identified: authentication failed, so 401.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `hasRole("ADMIN")` look for in the user's authorities?
:::
- [ ] ADMIN
- [x] ROLE_ADMIN
- [ ] admin
:::explain
Roles are authorities with the `ROLE_` prefix. `.roles("ADMIN")` adds it when you build the user, and
`hasRole("ADMIN")` adds it when it checks.
:::
:::

:::step{type=deep-dive title="Method security and tokens"}
Rules by URL are a good start. With `@EnableMethodSecurity`, you can also guard methods directly:
`@PreAuthorize("hasRole('ADMIN')")` on a service method protects it no matter which URL calls it. For
public APIs, `spring-boot-starter-oauth2-resource-server` validates JWT access tokens issued by an
identity provider (Keycloak, Auth0, Google), so the API never sees passwords at all.
:::

:::step{type=recap title="Chapter done"}
- 401: who are you? 403: you may not do this.
- A `SecurityFilterChain` bean holds the rules; the first matching rule decides.
- HTTP Basic sends credentials with every request; CSRF is off for APIs without cookies.
- Passwords are stored hashed in real apps; `{noop}` is for labs only.
:::
