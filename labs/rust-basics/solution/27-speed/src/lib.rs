//! Chapter 27: speed. Parsing a quarter of a year of logs, without copying a single field.
use std::collections::HashMap;

/// "T07,2026-11-24 10:10,12.4,2100" gives Some(("T07", 2100.0)): the turbine is a slice of the line.
pub fn turbine_and_power(line: &str) -> Option<(&str, f64)> {
    let (turbine, rest) = line.split_once(',')?;
    let (_, power) = rest.rsplit_once(',')?;
    Some((turbine, power.trim().parse().ok()?))
}

/// Energy per turbine in kWh (ten minutes a reading). The keys borrow from the text: no String per line.
pub fn energy_by_turbine(text: &str) -> HashMap<&str, f64> {
    let mut totals = HashMap::new();
    for line in text.lines() {
        if let Some((turbine, kw)) = turbine_and_power(line) {
            *totals.entry(turbine).or_insert(0.0) += kw * 10.0 / 60.0;
        }
    }
    totals
}
