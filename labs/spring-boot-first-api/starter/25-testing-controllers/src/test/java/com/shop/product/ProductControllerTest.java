package com.shop.product;

import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;

// TODO (task controller_test): test ProductController without starting the whole app. Use MockMvc, and
// replace ProductService with a mock (@MockitoBean). Write at least two tests:
//   GET /products/1 answers 200 with the product's name, when the service finds it;
//   GET /products/99 answers 404, when the service finds nothing.
// TODO (task catches_bug): the check also runs your tests against a broken controller. They must fail there.
@WebMvcTest(ProductController.class)
class ProductControllerTest {
}
