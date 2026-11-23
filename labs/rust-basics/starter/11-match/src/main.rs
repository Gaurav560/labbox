// Chapter 11: run it with  cargo run
use ch11_match::{describe, parse_line, Status};

fn main() {
    for status in [Status::Calm, Status::Generating { kw: 2500.0 }, Status::Generating { kw: 1312.4 },
                   Status::StormStop, Status::Fault(512), Status::Fault(204)] {
        println!("{status:?} -> {}", describe(&status));
    }

    let log = "T07,2026-11-24 10:10,12.4,2100
T07,2026-11-24 10:20,12.9
T07,2026-11-24 10:30,windy,2180
T07,2026-11-24 10:40,13.1,2210
T07,2026-11-24 10:50,13.4,22O0
T07,2026-11-24 11:00,13.0,2190";
    let mut kept = 0;
    for (n, line) in log.lines().enumerate() {
        match parse_line(line) {
            Some(r) => {
                kept += 1;
                println!("line {}: {} kW at {}", n + 1, r.power_kw, r.time);
            }
            None => println!("line {}: skipped: {line:?}", n + 1),
        }
    }
    println!("{kept} of 6 lines kept");

    if let Some(r) = parse_line("T12,2026-11-24 10:10,3.1,60") {
        println!("T12 is at {} m/s", r.wind_ms);
    }
}
