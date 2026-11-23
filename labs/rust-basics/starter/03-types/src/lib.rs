//! Chapter 3: Rust's basic types: integers, floats, booleans, characters, tuples and arrays.

/// Energy in kilowatt-hours made at a steady power (kW) for some minutes.
pub fn energy_kwh(power_kw: u32, minutes: u32) -> f64 {
    // TODO (task energy_kwh): turn both numbers into f64 with `as f64`, multiply them, and divide by 60.0.
    todo!()
}

/// One reading as text, from a (turbine number, wind speed in m/s, power in kW) tuple:
/// (7, 12.43, 2100) becomes "T07: 12.4 m/s, 2100 kW".
pub fn describe(reading: (u8, f64, u32)) -> String {
    // TODO (task describe): take the tuple apart with  let (turbine, wind, power) = reading;  and return
    //   format!("T{turbine:02}: {wind:.1} m/s, {power} kW").
    todo!()
}
