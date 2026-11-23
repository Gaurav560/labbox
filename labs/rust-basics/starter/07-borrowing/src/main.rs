// Chapter 7: run it with  cargo run
use ch07_borrowing::{average_power, cap_readings};

fn main() {
    let mut log = vec![2100.0, 2250.0, 9999.0, 1980.0];
    println!("T07: {log:?}, average {:.0} kW", average_power(&log));

    cap_readings(&mut log, 2500.0); // the meter glitch, 9999 kW, is capped at the rated 2500
    println!("capped: {log:?}, average {:.0} kW", average_power(&log));

    let first = &log[0];
    let last = &log[log.len() - 1];
    println!("first {first} kW, last {last} kW, still {} readings", log.len());
}
