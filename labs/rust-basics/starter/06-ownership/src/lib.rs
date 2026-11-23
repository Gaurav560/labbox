//! Chapter 6: ownership. Every value has one owner; giving it away is a move.

/// Two copies of a turbine's power log: one to keep working with, one as a backup.
pub fn with_backup(log: Vec<f64>) -> (Vec<f64>, Vec<f64>) {
    // TODO (task fix_moved_value): this does not compile: `let backup = log;` MOVES the vector into backup, so
    //   `log` cannot be used on the next line. Make backup a real copy with log.clone().
    let backup = log;
    (log, backup)
}

/// Takes ownership of the log, adds one reading in kW, and gives the log back.
pub fn add_reading(mut log: Vec<f64>, kw: f64) -> Vec<f64> {
    // TODO (task add_reading): push kw onto the log with log.push(kw), then give the log back (last expression).
    todo!()
}
