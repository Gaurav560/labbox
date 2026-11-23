// Chapter 5: run it with  cargo run
use ch05_control_flow::{first_storm_hour, hours_generating, status};

fn main() {
    for wind in [1.8, 3.0, 12.4, 24.9, 25.0, 31.2] {
        println!("{wind:>4} m/s: {}", status(wind));
    }

    // Monday at turbine T12, one reading an hour: a calm night, a windy day, a storm in the evening.
    let monday = [
        2.1, 1.8, 1.5, 2.4, 3.1, 4.0, 5.6, 7.2, 8.8, 10.1, 11.5, 12.0,
        12.8, 13.4, 14.9, 16.2, 19.8, 23.5, 26.1, 28.4, 22.0, 15.3, 9.7, 6.2,
    ];
    println!("Hours generating: {}", hours_generating(monday));
    match first_storm_hour(monday) {
        Some(hour) => println!("First storm stop at {hour}:00"),
        None => println!("No storm today"),
    }

    let mut tries = 0;
    let reply = loop {
        tries += 1;
        if tries == 3 {
            break "T12 answered";
        }
    };
    println!("{reply} after {tries} tries");
}
