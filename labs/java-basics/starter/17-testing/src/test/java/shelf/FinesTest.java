// Chapter 17: tests for the late fee. One example is here; the rest are yours to write.
package shelf;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class FinesTest {
    @Test
    void onTimeIsFree() {
        assertEquals(0, Fines.lateFee(0));
    }

    // TODO (task test_late_fee): more tests, so that any wrong change to lateFee makes at least one fail.
}
