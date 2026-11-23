// Chapter 8: run it with  cargo run
use ch08_slices_and_strings::{last_hour, turbine_id, wind_of};

fn main() {
    let lines = [
        "T07,2026-11-24 10:10,12.4,2100",
        "T12,2026-11-24 10:10,3.1,60",
        "T31,2026-11-24 10:10,25.6,0",
    ];
    for line in lines {
        println!("{} at {} m/s", turbine_id(line), wind_of(line));
    }

    let day: Vec<f64> = (1..=10).map(|i| 1800.0 + 50.0 * i as f64).collect();
    println!("last hour: {:?}", last_hour(&day));
    println!("last hour of 3: {:?}", last_hour(&day[..3]));

    let site = String::from("Kutch Coast Wind Farm"); // a String: owns its text, can grow
    let short: &str = &site[..11]; // a &str: borrows part of it
    println!("{short} ({} bytes of {})", short.len(), site.len());

    let price = "₹4.20 per unit";
    println!("{} characters, {} bytes", price.chars().count(), price.len());
}
