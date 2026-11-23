// Chapter 3: run it with  cargo run
use ch03_types::{describe, energy_kwh};

fn main() {
    let readings = [(7, 12.43, 2100), (12, 3.05, 40), (31, 24.96, 2500)];
    for reading in readings {
        println!("{}", describe(reading));
    }
    println!("2100 kW for 10 minutes: {:.1} kWh", energy_kwh(2100, 10));
    println!("2500 kW for a day: {} kWh", energy_kwh(2500, 24 * 60));

    let faults_today: u8 = 250;
    println!("u8 holds 0 to {}, so 250 + 10 does not fit: {:?}", u8::MAX, faults_today.checked_add(10));
    println!("is 25 m/s a storm? {}", 25.0 >= 25.0);
    println!("the farm's code letter: {}", 'K');
}
