package com.shop.product;

import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

// TODO (task repository_test): test the repository against a real (in-memory) database. Save a few
// products of two categories in the test, then check that findByCategoryOrderByNameAsc returns only
// that category, sorted by name. Use @Autowired ProductRepository; @DataJpaTest starts only JPA.
// TODO (task catches_query_bug): the check also runs your test against a repository whose query sorts the
// wrong way. Your test must fail there.
@DataJpaTest
class ProductRepositoryTest {
}
