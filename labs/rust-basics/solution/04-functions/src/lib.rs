//! Chapter 4: functions, parameters, return values, and expressions.
use std::f64::consts::PI;

/// How fast the tip of a blade moves, in metres per second.
pub fn tip_speed(rotor_rpm: f64, blade_m: f64) -> f64 {
    2.0 * PI * blade_m * rotor_rpm / 60.0
}

/// The most energy a turbine could make running at full power for some hours, in MWh.
pub fn max_energy_mwh(rated_kw: f64, hours: f64) -> f64 {
    rated_kw * hours / 1_000.0
}

/// Capacity factor: the energy made, as a percentage of the most that could have been made.
pub fn capacity_factor(energy_mwh: f64, rated_kw: f64, hours: f64) -> f64 {
    energy_mwh / max_energy_mwh(rated_kw, hours) * 100.0
}
