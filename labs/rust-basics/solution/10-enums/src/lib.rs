//! Chapter 10: enums and Option.

/// What a turbine is doing. Each variant can carry its own data.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Status {
    Calm,
    Generating { kw: f64 },
    StormStop,
    Fault(u16),
}

/// The status of a turbine from its wind, its power, and its fault code if it reported one.
pub fn classify(wind_ms: f64, power_kw: f64, fault: Option<u16>) -> Status {
    match fault {
        Some(code) => Status::Fault(code),
        None => {
            if wind_ms < 3.0 {
                Status::Calm
            } else if wind_ms >= 25.0 {
                Status::StormStop
            } else {
                Status::Generating { kw: power_kw }
            }
        }
    }
}

/// The highest reading in a log, or None for an empty log (there is no peak of nothing).
pub fn peak_power(log: &[f64]) -> Option<f64> {
    if log.is_empty() {
        return None;
    }
    let mut peak = log[0];
    for &kw in log {
        if kw > peak {
            peak = kw;
        }
    }
    Some(peak)
}
