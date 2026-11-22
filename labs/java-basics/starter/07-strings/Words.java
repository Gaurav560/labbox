// Chapter 7: strings.
public class Words {
    // TODO (task count_words): words are separated by spaces, tabs or new lines; "" has 0 words.
    public static int countWords(String text) {
        return 0;
    }

    // TODO (task clean_name): e.g. "  riya   SHARMA " is "Riya Sharma".
    public static String cleanName(String raw) {
        return "";
    }

    public static void main(String[] args) {
        System.out.println(countWords("Java is fun"));
        System.out.println(countWords("  lots   of   spaces  "));
        System.out.println("[" + cleanName("  riya   SHARMA ") + "]");
    }
}
