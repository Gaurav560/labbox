:::step{type=story title="Who is calling, and may they?"}
Right now, anyone who can reach the Shop API can read the sales report and delete products. There is no login,
no difference between a customer, a staff member and the owner. A real API must answer two questions for every
request: **who is calling?** and **are they allowed to do this?**

Spring Security answers both. It is powerful, and it has a reputation for being confusing, mostly because it does
a lot by default and beginners do not know where to look. This chapter goes step by step: what happens when you
add it, how its rules work, and why the details (rule order, CSRF, password storage) matter.

:::mission
Keep the product list public, require a login for everything else, and let only admins delete products.
:::
:::

:::step{type=concept title="Two questions, two status codes"}
Security has two separate parts, and HTTP has a status code for each:

- **Authentication**: *who are you?* The client proves its identity, usually with a username and password or a
  token. If it cannot (no credentials, wrong password), the answer is **401 Unauthorized**. (A confusing old name:
  401 really means "not authenticated".)
- **Authorization**: *are you allowed to do this?* The client is known, but this action is not for them. A staff
  member trying to delete products gets **403 Forbidden**.

Keep them apart in your head: 401 means "I do not know who you are"; 403 means "I know who you are, and no".
:::

:::step{type=try title="Add Spring Security, and everything locks" file="28-security/pom.xml"}
This chapter's project has `spring-boot-starter-security` in its pom, and no security configuration yet. Start it:

```bash run
cd 28-security && mvn -q -o package -DskipTests && java -jar target/security.jar
```

Look in the start-up log:

```text
Using generated security password: 38a8cb9a-e719-4d31-bb1f-6485bfc1adcd
This generated password is for development use only. Your security configuration must be updated before running
your application in production.
```

Then try the product list, which should be public:

```bash run
curl -i localhost:8080/products
```

```text
HTTP/1.1 401
WWW-Authenticate: Basic realm="Realm"
X-Content-Type-Options: nosniff
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
```

**Everything** is locked. That is Spring Boot's secure default (auto-configuration again, chapter 8): add the
security starter and every endpoint requires a login, with one user called `user` and a random password printed at
start-up. Locked by default is the right default, but it is not what the shop wants. Notice the extra headers too:
Spring Security also adds protective headers to every response, for free.

`WWW-Authenticate: Basic` tells the client: "authenticate with HTTP Basic". Let's see what that is.
:::

:::step{type=concept title="HTTP Basic, and why it needs HTTPS"}
**HTTP Basic** is the simplest way to send a login: the client adds a header to **every** request:

```text
Authorization: Basic c3RhZmY6c3RhZmYxMjM=
```

That strange text is just `staff:staff123` (username, colon, password) written in **Base64**, an encoding that
turns any bytes into plain letters. curl builds it for you with `-u staff:staff123`.

Base64 is **not encryption**: anyone can turn it back into `staff:staff123` in a second. So Basic is only safe
over **HTTPS**, where the whole request is encrypted on the wire. That holds for every login method, really: never
send credentials over plain HTTP outside your own machine.

Basic is fine for internal tools and for learning. Public APIs usually use **tokens** (OAuth2, JWT): the user logs in
once with an identity provider and the client sends a short-lived token instead of a password. They plug into the
same filter chain you are about to configure.
:::

:::step{type=concept title="The security filter chain"}
Spring Security is a chain of **filters** (chapter 18) that every request passes **before** it reaches the
DispatcherServlet:

:::diagram{name="security-chain"}
Every request passes the filters first; only allowed requests reach the controller.
:::

You describe what it should do with a **`SecurityFilterChain`** bean, built from an `HttpSecurity` object:

```java
@Configuration
public class LibrarySecurity {

    @Bean
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        return http
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.GET, "/books/**").permitAll()     // rule 1
                        .requestMatchers("/librarian/**").hasRole("LIBRARIAN")        // rule 2
                        .anyRequest().authenticated())                                // rule 3
                .httpBasic(Customizer.withDefaults())                                 // logins by HTTP Basic
                .build();
    }
}
```

The `authorizeHttpRequests` part is a list of **rules**, checked **top to bottom**, and **the first rule that matches
the request decides**:

- `requestMatchers(HttpMethod.GET, "/books/**").permitAll()`: anyone may GET books, even without a login.
- `requestMatchers("/librarian/**").hasRole("LIBRARIAN")`: those paths need a logged-in user with that role.
- `anyRequest().authenticated()`: everything else needs a login (any role).

Because the first match wins, put **specific rules first** and `anyRequest()` **last**. (Spring Security even refuses
to start if you put rules after `anyRequest()`, since they could never apply.)
:::

:::step{type=example title="Worked example: who gets in"}
With the library rules above, and two users (meera, a LIBRARIAN, and ravi, a READER), follow four requests:

:::trace{title="Who gets in"}
| request | user | first rule that matches | answer |
|---|---|---|---|
| GET /books/7 | nobody | GET /books/** permitAll | 200 |
| GET /librarian/loans | nobody | /librarian/** hasRole | 401: who are you? |
| GET /librarian/loans | ravi (READER) | /librarian/** hasRole | 403: not for you |
| GET /librarian/loans | meera (LIBRARIAN) | /librarian/** hasRole | 200 |
:::

Users can come from a database, an identity provider or LDAP. For learning, Spring Security can keep them in memory:

```java
@Bean
InMemoryUserDetailsManager users() {
    return new InMemoryUserDetailsManager(
            User.withUsername("meera").password("{noop}books1").roles("LIBRARIAN").build(),
            User.withUsername("ravi").password("{noop}read2").roles("READER").build());
}
```

Defining your own users makes the generated password disappear (the default backs off, chapter 8 again). The
`{noop}` prefix says "this password is stored as plain text": acceptable in a lab, never in a real system (see the
Go deeper step).
:::

:::step{type=concept title="CSRF, and why this API turns it off"}
One more default, which trips up nearly everyone building an API: **CSRF protection**.

**CSRF** (cross-site request forgery) is an attack on **browsers**: a malicious web page makes your browser send a
request to a site where you are logged in, and the browser helpfully attaches your login cookie. To block it,
Spring Security requires a secret **CSRF token** on every `POST`, `PUT`, `PATCH` and `DELETE`. A request without the
token gets **403**, even with the right password.

That protection only makes sense when the login travels in a **cookie** that the browser attaches by itself. An API
where every client sends its credentials explicitly in the `Authorization` header (like ours, with Basic, or with
tokens) is not exposed to that attack. So APIs like this switch it off:

```java
.csrf(csrf -> csrf.disable())
```

If you forget, the symptom is confusing: GETs work, and every DELETE answers 403, even for an admin. Keep CSRF on for
classic websites with login forms and session cookies.
:::

:::step{type=task task=public_and_protected title="Your turn: a public list, a protected rest"}
In `28-security/src/main/java/com/shop/SecurityConfig.java`, define two beans:

1. A **`SecurityFilterChain`**: `GET /products` open to everyone (`permitAll`); any other request needs a login;
   logins by **HTTP Basic**; **CSRF off**.
2. An **`InMemoryUserDetailsManager`** with two users: `staff` / `staff123` with role `STAFF`, and `admin` /
   `admin123` with role `ADMIN` (passwords prefixed with `{noop}`).

Rebuild, run, and knock on every door:

```bash run
curl -i localhost:8080/products; echo; curl -i localhost:8080/admin/report; echo; curl -u staff:staff123 localhost:8080/admin/report; echo; curl -i -u staff:nope localhost:8080/admin/report
```

You should see `200` with the products, `401`, `Sales today: 42 orders`, and `401` for the wrong password. The
generated password is gone from the log. Press **Check**.
:::

:::step{type=concept title="Roles"}
A **role** is a label on a user that rules can check: `STAFF`, `ADMIN`, `LIBRARIAN`. `hasRole("ADMIN")` lets in only
users with that role; `hasAnyRole("STAFF", "ADMIN")` lets in either.

Combine a method and a path in one rule to protect a single action:

```java
.requestMatchers(HttpMethod.DELETE, "/books/**").hasRole("LIBRARIAN")
```

Readers can still GET books (another rule allows that), but only librarians can delete them. The order matters again:
this rule must come **before** a broader rule that would match the same request first.

(Behind the scenes, a role is stored as an **authority** named `ROLE_ADMIN`. `.roles("ADMIN")` adds the prefix when
you build the user, and `hasRole("ADMIN")` adds it when it checks, so you rarely see it. You will, in some error
messages.)
:::

:::step{type=task task=admin_only title="Your turn: only admins delete"}
Add a rule so that only **ADMIN** may **DELETE `/products/{id}`** (use the pattern `/products/**`). A logged-in
STAFF user gets **403**.

Rebuild, run, and try both users:

```bash run
curl -i -X DELETE -u staff:staff123 localhost:8080/products/1; echo; curl -i -X DELETE -u admin:admin123 localhost:8080/products/1
```

`403` for staff (known, but not allowed), `204` for admin. If admin also gets 403, check that CSRF is off. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
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

:::step{type=predict title="Quick check (2 of 3)"}
:::question
CSRF is on (the default), and an admin sends `DELETE /products/1` with curl and correct Basic credentials. What happens?
:::
- [ ] 204: the admin is allowed
- [x] 403: no CSRF token was sent
- [ ] 401
:::explain
With CSRF on, every state-changing request needs a CSRF token, whoever sends it. APIs that authenticate with headers
switch CSRF off.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
The rules are `.anyRequest().authenticated()` first, then `.requestMatchers(GET, "/products").permitAll()`. What happens?
:::
- [ ] GET /products is public
- [x] Spring Security refuses to start: nothing can come after anyRequest()
- [ ] Every request is public
:::explain
The first matching rule decides, and `anyRequest()` matches everything, so a rule after it could never apply. Spring
Security reports that at start-up.
:::
:::

:::step{type=deep-dive title="Go deeper: storing passwords, method security, and tokens"}
**Never store plain passwords.** Real systems store a **hash**: a one-way scramble, so even someone who steals the
database cannot read the passwords. Spring Security's `PasswordEncoder` (with **BCrypt**) does it:
`passwordEncoder.encode("staff123")` gives something like `$2a$10$...`, stored as `{bcrypt}$2a$10$...`. At login,
Spring hashes what the user typed and compares.

**Method security.** With `@EnableMethodSecurity`, you can protect service methods directly:
`@PreAuthorize("hasRole('ADMIN')")`. Then the rule holds whichever URL calls the method.

**Who is logged in?** A controller method can take `@AuthenticationPrincipal UserDetails user` (or `Principal`) to know
who is calling, for example to show "my orders".

**Tokens.** For public APIs, `spring-boot-starter-oauth2-resource-server` checks **JWT** access tokens issued by an
identity provider (Keycloak, Auth0, Google, Azure AD). Your API never sees passwords at all. The production course
builds this.
:::

:::step{type=recap title="What you can do now"}
You can now secure an API:

- **401** = not authenticated (who are you?); **403** = authenticated but not allowed.
- Adding the security starter locks **everything** by default, with a generated password.
- A **`SecurityFilterChain`** bean: `authorizeHttpRequests` rules, checked top to bottom, **first match wins**
  (`permitAll`, `authenticated`, `hasRole`, `hasAnyRole`); specific rules first, `anyRequest()` last.
- **HTTP Basic** sends `username:password` in Base64 on every request: only over **HTTPS**.
- **CSRF** protects cookie-based browser logins; header-authenticated APIs **disable** it.
- Users in memory for learning; hashed passwords (**BCrypt**) and tokens (**JWT**) in real systems.

:::photo{src="/lesson-images/spring/spring-28-notes.webp" alt="Handwritten notes about Security: 401 = who are you?, 403 = not allowed, SecurityFilterChain: first match wins, HTTP Basic only over HTTPS, BCrypt for passwords" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 29: the Shop API is not alone. Calling other services, and surviving when they are slow.
:::
