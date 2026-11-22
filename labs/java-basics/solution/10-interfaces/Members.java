// Chapter 10: inheritance. A student is a member with a smaller limit.
public class Members {
    static class Member {
        final String name;

        Member(String name) {
            this.name = name;
        }

        int maxBooks() {
            return 5;
        }

        String describe() {
            return name + " may borrow " + maxBooks() + " books";
        }
    }

    static class Student extends Member {
        Student(String name) {
            super(name);
        }

        @Override
        int maxBooks() {
            return 2;
        }
    }

    public static void main(String[] args) {
        Member asha = new Member("Asha");
        Member kabir = new Student("Kabir");
        System.out.println(asha.describe());
        System.out.println(kabir.describe());
    }
}
