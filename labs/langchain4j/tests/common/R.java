package com.setu.check;

/** Prints one @@RESULT line per task. Checks never fail the build: every task always gets a result. */
public final class R {
    private R() {}

    static String esc(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> b.append("\\\"");
                case '\\' -> b.append("\\\\");
                case '\n' -> b.append("\\n");
                case '\r' -> { }
                case '\t' -> b.append("\\t");
                default -> b.append(c < 0x20 ? ' ' : c);
            }
        }
        return b.toString();
    }

    public static void pass(String task, String message) {
        System.out.println("@@RESULT {\"task\": \"" + esc(task) + "\", \"passed\": true, \"message\": \"" + esc(message) + "\"}");
    }

    public static void fail(String task, String message) {
        System.out.println("@@RESULT {\"task\": \"" + esc(task) + "\", \"passed\": false, \"message\": \"Not yet: " + esc(message) + "\"}");
    }

    public static void fail(String task, String message, String expected, String actual) {
        System.out.println("@@RESULT {\"task\": \"" + esc(task) + "\", \"passed\": false, \"message\": \"Not yet: " + esc(message)
                + "\", \"expected\": \"" + esc(expected) + "\", \"actual\": \"" + esc(actual) + "\"}");
    }

    /** Runs one task's check; anything unexpected becomes a clear failure for that task only. */
    public static void task(String task, Check check) {
        try {
            check.run();
        } catch (Throwable t) {
            fail(task, "the check stopped with " + t.getClass().getSimpleName() + ": " + String.valueOf(t.getMessage()).lines().findFirst().orElse(""));
        }
    }

    @FunctionalInterface
    public interface Check {
        void run() throws Exception;
    }
}
