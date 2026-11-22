// Chapter 17: tests for Renewals. Run them with: mvn -o -q test
package shelf;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class RenewalsTest {
    @Test
    void firstRenewalIsAllowed() {
        assertTrue(Renewals.canRenew(0, false));
    }

    @Test
    void reservedBooksCannotBeRenewed() {
        assertFalse(Renewals.canRenew(0, true));
    }

    @Test
    void noThirdRenewal() {
        assertFalse(Renewals.canRenew(2, false), "two renewals already: a third is not allowed");
    }
}
