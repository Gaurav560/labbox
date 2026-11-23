//! Chapter 5: if, loop, while and for.

/// What a turbine does at a wind speed: below 3 m/s it waits, from 25 m/s it stops to protect itself.
pub fn status(wind_ms: f64) -> &'static str {
    if wind_ms < 3.0 {
        "too calm"
    } else if wind_ms < 25.0 {
        "generating"
    } else {
        "storm stop"
    }
}

/// How many of a day's 24 hourly wind speeds were good for generating.
pub fn hours_generating(winds: [f64; 24]) -> u32 {
    let mut hours = 0;
    for wind in winds {
        if status(wind) == "generating" {
            hours += 1;
        }
    }
    hours
}

/// The first hour (0 to 23) with a storm stop, if there was one.
pub fn first_storm_hour(winds: [f64; 24]) -> Option<usize> {
    let mut hour = 0;
    while hour < winds.len() {
        if status(winds[hour]) == "storm stop" {
            return Some(hour);
        }
        hour += 1;
    }
    None
}
