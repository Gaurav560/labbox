// Chapter 16: the list of books, in its own package.
package shelf.catalog;

import java.util.ArrayList;
import java.util.List;

public class Catalog {
    private final List<String> titles = new ArrayList<>();

    public void add(String title) {
        titles.add(title);
    }

    public int size() {
        return titles.size();
    }
}
