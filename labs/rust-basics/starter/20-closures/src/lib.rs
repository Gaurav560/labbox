//! Chapter 20: closures. Small functions written in place, that can capture values around them.

#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

impl Reading {
    pub fn new(turbine: &str, wind_ms: f64, power_kw: f64) -> Reading {
        Reading { turbine: turbine.to_string(), wind_ms, power_kw }
    }
}

/// A rule that is true for a reading below `limit_kw` while the wind is strong enough to generate well.
/// The closure keeps its own copy of limit_kw (move), so it can outlive this function.
pub fn below(limit_kw: f64) -> impl Fn(&Reading) -> bool {
    // TODO (task below): return a closure that captures limit_kw:
    //   move |r: &Reading| r.wind_ms >= 6.0 && r.power_kw < limit_kw
    move |_r: &Reading| todo!()
}

/// One alert line per (rule, reading) that matches, like "T12: low power". Rules are named closures in boxes.
pub fn alerts(readings: &[Reading], rules: &[(&str, Box<dyn Fn(&Reading) -> bool>)]) -> Vec<String> {
    // TODO (task alerts): for each reading r, and each (name, rule) in rules, call rule(r); when it is true,
    //   push format!("{}: {}", r.turbine, name). Return the lines.
    let _ = (readings, rules);
    todo!()
}
