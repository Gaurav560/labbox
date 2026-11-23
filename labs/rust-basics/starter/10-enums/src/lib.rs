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
    // TODO (task classify): match fault { Some(code) => Status::Fault(code), None => ... }. With no fault: below
    //   3.0 m/s Status::Calm, from 25.0 Status::StormStop, otherwise Status::Generating { kw: power_kw }.
    todo!()
}

/// The highest reading in a log, or None for an empty log (there is no peak of nothing).
pub fn peak_power(log: &[f64]) -> Option<f64> {
    // TODO (task peak_power): return None for an empty log. Otherwise start with let mut peak = log[0];, keep the
    //   largest in a loop (for &kw in log), and return Some(peak).
    todo!()
}
