// Chapter 19: run it with  cargo run
use ch19_lifetimes::{stronger, LogLine, Reading};

fn main() {
    let t07 = Reading::new("T07", 12.4, 2100.0);
    let t12 = Reading::new("T12", 7.5, 140.0);
    println!("stronger: {}", stronger(&t07, &t12).turbine);

    let log = String::from("T07,2026-11-24 10:10,12.4,2100\nT12,2026-11-24 10:10,7.5,140\nbroken line");
    for line in log.lines() {
        match LogLine::parse(line) {
            Some(l) => println!("{l:?}"),
            None => println!("not a log line: {line:?}"),
        }
    }
}
