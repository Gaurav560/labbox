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
    // TODO (task total_energy): one chain: readings.iter().map(|r| r.power_kw * 10.0 / 60.0).sum::<f64>(),
    //   then divide by 1_000.0 (kWh to MWh).
    todo!()
}

/// The ids of readings that make less than 80% of the power curve's 2500 kW in winds of 12 m/s or more, in order.
pub fn weak_in_strong_wind(readings: &[Reading]) -> Vec<&str> {
    // TODO (task weak_turbines): readings.iter(), keep (filter) winds from 12.0 to below 25.0, keep power below
    //   2_000.0, map each to r.turbine.as_str(), and collect() into the Vec.
    let _ = readings;
    todo!()
}

/// The same total, with a plain loop: for the speed comparison in main.rs.
pub fn total_energy_loop(readings: &[Reading]) -> f64 {
    let mut total = 0.0;
    for i in 0..readings.len() {
        total += readings[i].power_kw * 10.0 / 60.0;
    }
    total / 1_000.0
}
