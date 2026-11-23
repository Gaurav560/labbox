import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

import com.sun.net.httpserver.HttpServer;

/**
 * A pretend supplier for chapter 29, on port 9099. Run it in its own terminal with:  java FakeSupplier.java
 *   GET /stock/KUL-1    -> 200 {"sku": "KUL-1", "available": 120}   (any sku works the same)
 *   GET /stock/MISSING  -> 404: the supplier does not stock it
 *   GET /stock/SLOW     -> answers after 3 seconds: a supplier having a bad day
 */
public class FakeSupplier {

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(9099), 0);
        server.createContext("/stock/", exchange -> {
            String sku = exchange.getRequestURI().getPath().substring("/stock/".length());
            System.out.println("Supplier: someone asked for " + sku);
            int code = 200;
            String body = "{\"sku\": \"" + sku + "\", \"available\": 120}";
            if (sku.equals("MISSING")) {
                code = 404;
                body = "{\"error\": \"not stocked\"}";
            } else if (sku.equals("SLOW")) {
                try {
                    Thread.sleep(3000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.sendResponseHeaders(code, bytes.length);
            exchange.getResponseBody().write(bytes);
            exchange.close();
        });
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
        System.out.println("Fake supplier listening on port 9099. Stop it with Ctrl+C.");
    }
}
