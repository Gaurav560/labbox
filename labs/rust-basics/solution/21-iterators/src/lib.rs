//! Chapter 21: iterators. Chains of small steps that compile to tight loops.

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

/// Energy in MWh, if each reading held for ten minutes.
pub fn total_energy_mwh(readings: &[Reading]) -> f64 {
    readings.iter().map(|r| r.power_kw * 10.0 / 60.0).sum::<f64>() / 1_000.0
}

/// The ids of readings that make less than 80% of the power curve's 2500 kW in winds of 12 m/s or more, in order.
pub fn weak_in_strong_wind(readings: &[Reading]) -> Vec<&str> {
    readings
        .iter()
        .filter(|r| r.wind_ms >= 12.0 && r.wind_ms < 25.0)
        .filter(|r| r.power_kw < 2_000.0)
        .map(|r| r.turbine.as_str())
        .collect()
}

/// The same total, with a plain loop: for the speed comparison in main.rs.
pub fn total_energy_loop(readings: &[Reading]) -> f64 {
    let mut total = 0.0;
    for i in 0..readings.len() {
        total += readings[i].power_kw * 10.0 / 60.0;
    }
    total / 1_000.0
}
