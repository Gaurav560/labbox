// Chapter 7: two strings with the same text. Are they the same?
public class SameText {
    public static void main(String[] args) {
        String a = "riya";
        String b = new String("riya");
        System.out.println(a == b);
        System.out.println(a.equals(b));
    }
}
