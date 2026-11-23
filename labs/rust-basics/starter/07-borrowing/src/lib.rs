//! Chapter 7: borrowing. A reference lets a function use a value without taking it.

/// The average of a log of power readings in kW (0.0 for an empty log). Borrows the log: the caller keeps it.
pub fn average_power(log: &Vec<f64>) -> f64 {
    if log.is_empty() {
        return 0.0;
    }
    // TODO (task average_power): add up the readings (for kw in log { total += kw; }) and divide by
    //   log.len() as f64. The log is borrowed (&Vec<f64>): read it, do not take it.
    todo!()
}

/// Caps every reading above max_kw at max_kw, in place: a meter glitch can report more than a turbine can make.
pub fn cap_readings(log: &mut Vec<f64>, max_kw: f64) {
    // TODO (task cap_readings): loop with  for kw in log.iter_mut()  (each kw is a &mut f64), and where
    //   *kw > max_kw, set *kw = max_kw. The * reaches through the reference to the number itself.
    todo!()
}
