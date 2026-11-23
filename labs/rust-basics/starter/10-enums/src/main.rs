// Chapter 10: run it with  cargo run
use ch10_enums::{classify, peak_power, Status};

fn main() {
    let turbines = [("T07", 12.4, 2100.0, None), ("T12", 2.1, 0.0, None), ("T19", 14.0, 0.0, Some(512)), ("T31", 25.6, 0.0, None)];
    for (id, wind, kw, fault) in turbines {
        let status = classify(wind, kw, fault);
        println!("{id}: {status:?}");
    }

    let monday = [2100.0, 2400.0, 2250.0];
    let tuesday: [f64; 0] = [];
    println!("Monday peak: {:?}", peak_power(&monday));
    println!("Tuesday peak: {:?}", peak_power(&tuesday));
    println!("Tuesday peak, or 0: {}", peak_power(&tuesday).unwrap_or(0.0));

    let s = Status::Generating { kw: 1800.0 };
    println!("is {s:?} a fault? {}", s == Status::Fault(512));
}
