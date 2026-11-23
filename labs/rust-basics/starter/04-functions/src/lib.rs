//! Chapter 4: functions, parameters, return values, and expressions.
use std::f64::consts::PI;

/// How fast the tip of a blade moves, in metres per second.
pub fn tip_speed(rotor_rpm: f64, blade_m: f64) -> f64 {
    // TODO (task tip_speed): one turn moves the tip 2 * PI * blade_m metres; it turns rotor_rpm times a minute.
    //   Return 2.0 * PI * blade_m * rotor_rpm / 60.0 as the last expression (no semicolon).
    todo!()
}

/// The most energy a turbine could make running at full power for some hours, in MWh.
pub fn max_energy_mwh(rated_kw: f64, hours: f64) -> f64 {
    rated_kw * hours / 1_000.0
}

/// Capacity factor: the energy made, as a percentage of the most that could have been made.
pub fn capacity_factor(energy_mwh: f64, rated_kw: f64, hours: f64) -> f64 {
    // TODO (task capacity_factor): divide energy_mwh by max_energy_mwh(rated_kw, hours), and multiply by 100.0.
    todo!()
}
