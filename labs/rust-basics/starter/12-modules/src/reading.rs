//! One log line. `crate::reading::Reading` from anywhere in this crate.

/// One line of a turbine's log, as one value with named fields.
#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub time: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

/// A log line as a Reading, or None if it is broken (chapter 11).
pub fn parse_line(line: &str) -> Option<Reading> {
    let parts: Vec<&str> = line.split(',').collect();
    let [turbine, time, wind, power] = parts[..] else {
        return None;
    };
    let Ok(wind_ms) = wind.trim().parse::<f64>() else {
        return None;
    };
    let Ok(power_kw) = power.trim().parse::<f64>() else {
        return None;
    };
    Some(Reading { turbine: turbine.to_string(), time: time.to_string(), wind_ms, power_kw })
}
