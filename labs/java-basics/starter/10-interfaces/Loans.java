// Chapter 10: one interface, two kinds of things a library lends. Shelf treats them the same way.
import java.util.List;

public class Loans {
    interface Lendable {
        String name();
        int loanDays();
    }

    record Book(String name) implements Lendable {
        public int loanDays() {
            return 21;
        }
    }

    record Dvd(String name) implements Lendable {
        public int loanDays() {
            return 7;
        }
    }

    public static void main(String[] args) {
        List<Lendable> desk = List.of(new Book("The Hobbit"), new Dvd("Planet Earth"), new Book("Dune"));
        for (Lendable item : desk) {
            System.out.println(item.name() + ": " + item.loanDays() + " days");
        }
    }
}
