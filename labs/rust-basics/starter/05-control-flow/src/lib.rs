//! Chapter 5: if, loop, while and for.

/// What a turbine does at a wind speed: below 3 m/s it waits, from 25 m/s it stops to protect itself.
pub fn status(wind_ms: f64) -> &'static str {
    // TODO (task status): below 3.0 return "too calm", below 25.0 "generating", otherwise "storm stop".
    //   Use if / else if / else as the last expression of the function.
    todo!()
}

/// How many of a day's 24 hourly wind speeds were good for generating.
pub fn hours_generating(winds: [f64; 24]) -> u32 {
    // TODO (task hours_generating): start a counter with  let mut hours = 0;  then
    //   for wind in winds { ... }  and add 1 when status(wind) is "generating". Return the counter.
    todo!()
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
