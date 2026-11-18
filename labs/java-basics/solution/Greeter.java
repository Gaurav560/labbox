public class Greeter {
    public static String greet(String name) {
        return "Hello, " + name + "!";
    }

    public static int longestWord(String sentence) {
        int best = 0;
        for (String word : sentence.split(" ")) {
            best = Math.max(best, word.length());
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(greet("Asha"));
    }
}
