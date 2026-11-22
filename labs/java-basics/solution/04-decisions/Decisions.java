// Chapter 4: making decisions.
public class Decisions {
    public static String grade(int marks) {
        if (marks < 0 || marks > 100) {
            return "Invalid";
        } else if (marks >= 80) {
            return "A";
        } else if (marks >= 60) {
            return "B";
        } else if (marks >= 40) {
            return "C";
        } else {
            return "F";
        }
    }

    public static boolean isLeapYear(int year) {
        return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    }

    public static void main(String[] args) {
        System.out.println(grade(80));
        System.out.println(isLeapYear(2100));
    }
}
