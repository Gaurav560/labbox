/** One UPI payment to a merchant, in paise (100 paise = 1 rupee). */
public record Payment(String merchant, long amountPaise) {}
