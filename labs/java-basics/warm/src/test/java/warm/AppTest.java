package warm;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class AppTest {
    @Test
    void twice() {
        assertEquals(42, App.twice(21));
        assertThrows(ArithmeticException.class, () -> Math.floorDiv(1, 0));
    }
}
