package com.shop.payments;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** Lists every payment method the shop accepts, for the checkout page. */
@RestController
public class GatewayController {

    // TODO (task all_gateways): ask Spring for ALL the PaymentGateway beans (a List) in a constructor,
    // and return their names sorted A to Z from GET /gateways.
    @GetMapping("/gateways")
    public List<String> gateways() {
        return List.of();
    }
}
