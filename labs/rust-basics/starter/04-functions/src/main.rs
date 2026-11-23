// Chapter 4: run it with  cargo run
use ch04_functions::{capacity_factor, max_energy_mwh, tip_speed};

fn main() {
    for rpm in [8.0, 12.0, 15.5] {
        let tip = tip_speed(rpm, 50.0);
        println!("{rpm} rpm with 50 m blades: tip at {tip:.1} m/s ({:.0} km/h)", tip * 3.6);
    }
    let hours = 24.0 * 30.0;
    println!("Most one turbine can make in 30 days: {} MWh", max_energy_mwh(2500.0, hours));
    for made in [612.0, 1_080.0, 1_800.0] {
        println!("{made} MWh in 30 days: capacity factor {:.1}%", capacity_factor(made, 2500.0, hours));
    }
}
