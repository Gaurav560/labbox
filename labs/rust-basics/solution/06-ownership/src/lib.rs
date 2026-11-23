//! Chapter 6: ownership. Every value has one owner; giving it away is a move.

/// Two copies of a turbine's power log: one to keep working with, one as a backup.
pub fn with_backup(log: Vec<f64>) -> (Vec<f64>, Vec<f64>) {
    let backup = log.clone();
    (log, backup)
}

/// Takes ownership of the log, adds one reading in kW, and gives the log back.
pub fn add_reading(mut log: Vec<f64>, kw: f64) -> Vec<f64> {
    log.push(kw);
    log
}
