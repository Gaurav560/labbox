// Chapter 15: run it with  cargo run
use std::error::Error;
use std::fs;

use ch15_errors::parse_reading;

fn main() -> Result<(), Box<dyn Error>> {
    let text = fs::read_to_string("data/t07.log")?; // a missing file ends main with an error, not a panic
    let mut good = 0;
    for (n, line) in text.lines().enumerate() {
        match parse_reading(line) {
            Ok(r) => {
                good += 1;
                println!("line {}: {} {} kW", n + 1, r.turbine, r.power_kw);
            }
            Err(why) => println!("line {}: {why}", n + 1),
        }
    }
    println!("{good} good readings");

    let missing = fs::read_to_string("data/t99.log");
    println!("t99: {:?}", missing.map(|text| text.len()));
    Ok(())
}
