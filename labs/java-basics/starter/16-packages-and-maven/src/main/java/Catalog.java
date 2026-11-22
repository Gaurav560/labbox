// Chapter 16: the list of books. It still lives in no package at all.
// TODO (task package_catalog): give it the package shelf.catalog and move it to src/main/java/shelf/catalog/.
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
