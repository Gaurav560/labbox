// A program that compiles perfectly, then stops while it runs. Run it and read Java's message.
public class Crash {
    public static void main(String[] args) {
        int books = 12;
        int shelves = 0;
        System.out.println("Books: " + books);
        System.out.println("Books per shelf: " + books / shelves);
        System.out.println("This line never runs.");
    }
}
