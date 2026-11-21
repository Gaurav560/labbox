// TODO (task component_scan): Spring never finds this class, because it is outside the package of
// ShopApiApplication (com.shop). Move it into a package under com.shop, for example com.shop.status.
package status;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class StatusController {

    @GetMapping("/status")
    public String status() {
        return "ok";
    }
}
