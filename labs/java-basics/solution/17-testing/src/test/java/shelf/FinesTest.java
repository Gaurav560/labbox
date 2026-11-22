// Chapter 17: tests for the late fee. One example is here; the rest are yours to write.
package shelf;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class FinesTest {
    @Test
    void onTimeIsFree() {
        assertEquals(0, Fines.lateFee(0));
    }

    @Test
    void twoRupeesADayForTheFirstWeek() {
        assertEquals(2, Fines.lateFee(1));
        assertEquals(14, Fines.lateFee(7));
    }

    @Test
    void fiveRupeesADayAfterAWeek() {
        assertEquals(19, Fines.lateFee(8));
        assertEquals(29, Fines.lateFee(10));
    }

    @Test
    void neverMoreThanAHundred() {
        assertEquals(99, Fines.lateFee(24));
        assertEquals(100, Fines.lateFee(25));
        assertEquals(100, Fines.lateFee(365));
    }

    @Test
    void negativeDaysAreRefused() {
        assertThrows(IllegalArgumentException.class, () -> Fines.lateFee(-1));
    }
}
