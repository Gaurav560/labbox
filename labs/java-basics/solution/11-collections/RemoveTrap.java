// Chapter 11: remove(1) on a list of numbers.
import java.util.ArrayList;
import java.util.List;

public class RemoveTrap {
    public static void main(String[] args) {
        List<Integer> fines = new ArrayList<>(List.of(5, 9, 1));
        fines.remove(1);
        System.out.println(fines);
        fines.remove(Integer.valueOf(5));
        System.out.println(fines);
    }
}
