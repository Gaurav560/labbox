//! Chapter 7: borrowing. A reference lets a function use a value without taking it.

/// The average of a log of power readings in kW (0.0 for an empty log). Borrows the log: the caller keeps it.
pub fn average_power(log: &Vec<f64>) -> f64 {
    if log.is_empty() {
        return 0.0;
    }
    let mut total = 0.0;
    for kw in log {
        total += kw;
    }
    total / log.len() as f64
}

/// Caps every reading above max_kw at max_kw, in place: a meter glitch can report more than a turbine can make.
pub fn cap_readings(log: &mut Vec<f64>, max_kw: f64) {
    for kw in log.iter_mut() {
        if *kw > max_kw {
            *kw = max_kw;
        }
    }
}
