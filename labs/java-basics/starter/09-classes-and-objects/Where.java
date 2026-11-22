// Chapter 9: a record holds plain values, and Java writes the boring parts for you.
public record Where(String title, int shelf) {
    public static void main(String[] args) {
        Where w = new Where("Dune", 3);
        System.out.println(w);
        System.out.println(w.title() + " " + w.shelf());
        System.out.println(w.equals(new Where("Dune", 3)));
    }
}
