// Chapter 13: one bad value does not stop the others.
public class Catch {
    public static void main(String[] args) {
        String[] typed = {"42", "twelve", "7"};
        for (String text : typed) {
            try {
                int age = Integer.parseInt(text);
                System.out.println(text + " -> " + age);
            } catch (NumberFormatException e) {
                System.out.println(text + " -> problem: " + e.getMessage());
            }
        }
        System.out.println("all done");
    }
}
