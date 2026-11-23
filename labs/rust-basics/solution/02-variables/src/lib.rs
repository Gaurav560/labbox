//! Chapter 2: variables, mutability, constants and shadowing.

/// One turbine's rated power: the most it can make, in kilowatts.
pub const RATED_POWER_KW: u32 = 2_500;

/// The farm's capacity in megawatts, for a number of turbines.
pub fn capacity_mw(turbines: u32) -> u32 {
    turbines * RATED_POWER_KW / 1_000
}

/// A wind speed as the anemometer writes it, like "  12.5 m/s", as a number: 12.5.
pub fn wind_speed(text: &str) -> f64 {
    let speed = text.trim();
    let speed = speed.trim_end_matches("m/s").trim();
    let speed: f64 = speed.parse().unwrap();
    speed
}
