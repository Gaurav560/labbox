// Chapter 2: run it with  cargo run
use ch02_variables::{capacity_mw, wind_speed, RATED_POWER_KW};

fn main() {
    println!("One turbine: {RATED_POWER_KW} kW");
    for turbines in [1, 10, 40] {
        println!("{turbines} turbines: {} MW", capacity_mw(turbines));
    }

    let mut online = 40;
    online -= 3; // three turbines stopped for maintenance
    println!("Online now: {online}, {} MW", capacity_mw(online));

    for text in ["12.5 m/s", "  3.2m/s ", "25 m/s"] {
        println!("{text:?} -> {}", wind_speed(text));
    }
}
