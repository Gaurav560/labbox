use ch07_borrowing::*;

#[test]
fn labbox_checks() {
    task("average_power", || {
        let log = vec![2100.0, 2250.0, 1950.0];
        let got = average_power(&log);
        if !close(got, 2100.0) {
            return Err(differs("Add up the readings and divide by log.len() as f64.", 2100.0, got));
        }
        if log.len() != 3 || average_power(&Vec::new()) != 0.0 {
            return Err(fail("An empty log should give 0.0, and the caller must keep its log."));
        }
        Ok("The function read the log through a reference; the caller still owns it.".into())
    });
    task("cap_readings", || {
        let mut log = vec![2100.0, 9999.0, 2500.0, 3100.5];
        cap_readings(&mut log, 2500.0);
        if log != vec![2100.0, 2500.0, 2500.0, 2500.0] {
            return Err(differs("Every reading above max_kw becomes max_kw, in the same vector (*kw = max_kw).", "[2100.0, 2500.0, 2500.0, 2500.0]", format!("{log:?}")));
        }
        Ok("A mutable borrow changed the caller's vector in place, without moving it.".into())
    });
}
