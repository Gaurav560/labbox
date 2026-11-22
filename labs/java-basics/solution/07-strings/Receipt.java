// Chapter 7: tidy a line typed in a hurry at the desk.
public class Receipt {
    public static void main(String[] args) {
        String typed = "   THE hobbit   ";
        System.out.println("[" + typed + "]");
        System.out.println("[" + typed.strip() + "]");
        System.out.println(typed.strip().toLowerCase());
        System.out.println(typed.length() + " " + typed.strip().length());
    }
}
