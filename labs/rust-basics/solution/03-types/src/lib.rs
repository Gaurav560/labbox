//! Chapter 3: Rust's basic types: integers, floats, booleans, characters, tuples and arrays.

/// Energy in kilowatt-hours made at a steady power (kW) for some minutes.
pub fn energy_kwh(power_kw: u32, minutes: u32) -> f64 {
    power_kw as f64 * minutes as f64 / 60.0
}

/// One reading as text, from a (turbine number, wind speed in m/s, power in kW) tuple:
/// (7, 12.43, 2100) becomes "T07: 12.4 m/s, 2100 kW".
pub fn describe(reading: (u8, f64, u32)) -> String {
    let (turbine, wind, power) = reading;
    format!("T{turbine:02}: {wind:.1} m/s, {power} kW")
}
