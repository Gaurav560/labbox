// Chapter 15: the words typed after the program's name arrive in args.
public class Args {
    public static void main(String[] args) {
        System.out.println(args.length + " words");
        for (int i = 0; i < args.length; i++) {
            System.out.println("args[" + i + "] = " + args[i]);
        }
        if (args.length == 0) {
            System.err.println("Usage: java Args.java <words>");
            System.exit(2);
        }
    }
}
