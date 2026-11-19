package com.paysetu;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MerchantController {

    static final List<String> MERCHANTS = List.of("Kirana King", "Brew Point", "Annapurna Mess");

    // TODO (task hello): GET /hello returns the text "Hello from PaySetu!"

    // TODO (task merchants): GET /merchants returns MERCHANTS sorted A to Z, as JSON
}
