package com.shop;

import org.springframework.context.annotation.Configuration;

// TODO (task public_and_protected): define a SecurityFilterChain bean: GET /products is open to everyone,
// everything else needs a login with HTTP Basic. Turn CSRF off (this is a stateless API). Define two
// users in memory (an InMemoryUserDetailsManager bean): staff / staff123 with role STAFF, and
// admin / admin123 with role ADMIN. Passwords must be encoded: use {noop} only here, in a lab.
// TODO (task admin_only): only ADMIN may DELETE /products/{id}; a logged-in STAFF user gets 403.
@Configuration
public class SecurityConfig {
}
