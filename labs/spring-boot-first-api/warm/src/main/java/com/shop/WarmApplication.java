package com.shop;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class WarmApplication {
    public static void main(String[] args) { SpringApplication.run(WarmApplication.class, args); }

    @Bean
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        return http.authorizeHttpRequests(a -> a.anyRequest().permitAll()).csrf(c -> c.disable()).build();
    }
}

@Entity
class Item {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id;
    @NotBlank String name;
}

interface ItemRepository extends JpaRepository<Item, Long> {}

@RestController
class HelloController {
    @GetMapping("/hello") String hello() { return "hello"; }
}
