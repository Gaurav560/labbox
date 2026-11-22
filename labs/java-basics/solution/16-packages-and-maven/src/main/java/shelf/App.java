// Chapter 16: Shelf's front door. It lives in the package shelf.
package shelf;

import shelf.catalog.Catalog;

public class App {
    public static void main(String[] args) {
        Catalog catalog = new Catalog();
        catalog.add("Dune");
        catalog.add("Emma");
        System.out.println("Shelf 1.0: " + catalog.size() + " books");
    }
}
