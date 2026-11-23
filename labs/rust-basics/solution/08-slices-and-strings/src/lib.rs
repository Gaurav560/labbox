//! Chapter 8: slices and strings. A slice is a borrowed view of part of a list or a text.

/// The turbine id at the start of a log line, without copying:
/// "T07,2026-11-24 10:10,12.4,2100" gives "T07".
pub fn turbine_id(line: &str) -> &str {
    match line.find(',') {
        Some(comma) => &line[..comma],
        None => line,
    }
}

/// The last hour of readings: the last 6 (one every ten minutes), or all of them if there are fewer.
pub fn last_hour(readings: &[f64]) -> &[f64] {
    let start = readings.len().saturating_sub(6);
    &readings[start..]
}

/// The wind speed, the third field of a log line, as a number.
pub fn wind_of(line: &str) -> f64 {
    line.split(',').nth(2).unwrap().trim().parse().unwrap()
}
