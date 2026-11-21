package com.shop.payments;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** Lists every payment method the shop accepts, for the checkout page. */
@RestController
public class GatewayController {

    private final List<PaymentGateway> all;

    public GatewayController(List<PaymentGateway> all) {
        this.all = all;
    }

    @GetMapping("/gateways")
    public List<String> gateways() {
        return all.stream().map(PaymentGateway::name).sorted().toList();
    }
}
