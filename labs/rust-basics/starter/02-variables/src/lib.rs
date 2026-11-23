//! Chapter 2: variables, mutability, constants and shadowing.

/// One turbine's rated power: the most it can make, in kilowatts.
pub const RATED_POWER_KW: u32 = 2_500;

/// The farm's capacity in megawatts, for a number of turbines.
pub fn capacity_mw(turbines: u32) -> u32 {
    // TODO (task capacity_mw): multiply the turbines by RATED_POWER_KW and divide by 1_000 (kW to MW).
    todo!()
}

/// A wind speed as the anemometer writes it, like "  12.5 m/s", as a number: 12.5.
pub fn wind_speed(text: &str) -> f64 {
    let speed = text.trim();
    // TODO (task wind_speed): shadow `speed` twice more: first remove the unit with
    //   speed.trim_end_matches("m/s").trim(), then turn the text into a number with
    //   let speed: f64 = speed.parse().unwrap();  and return it.
    todo!()
}
