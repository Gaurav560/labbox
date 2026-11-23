use ch16_error_types::*;

#[test]
fn labbox_checks() {
    task("error_enum", || {
        let e = ReadingError::TooMuchPower { kw: 9999.0 };
        if e.to_string() != "power 9999 kW is more than the turbine's 2500 kW" {
            return Err(differs("The message comes from #[error(\"...\")] on the variant.", "power 9999 kW is more than the turbine's 2500 kW", e.to_string()));
        }
        let got = parse_reading("T12,10:30,8.1,9999");
        if got != Err(ReadingError::TooMuchPower { kw: 9999.0 }) {
            return Err(differs("parse_reading should return TooMuchPower for a reading above 2,500 kW.", "Err(TooMuchPower { kw: 9999.0 })", got));
        }
        if parse_reading("T12,10:30,8.1,2500").is_err() {
            return Err(fail("Exactly 2,500 kW is allowed: only more than 2,500 is an error."));
        }
        Ok("A new kind of error, with its own message, that callers can match on.".into())
    });
}
