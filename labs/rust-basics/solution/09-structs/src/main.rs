// Chapter 9: run it with  cargo run
use ch09_structs::Reading;

fn main() {
    let first = Reading::from_line("T07,2026-11-24 10:10,12.4,2100");
    println!("{first:#?}");

    for line in [
        "T07,2026-11-24 10:10,12.4,2100",
        "T12,2026-11-24 10:10,7.5,140",
        "T19,2026-11-24 10:10,7.5,305",
        "T31,2026-11-24 10:10,25.6,0",
    ] {
        let r = Reading::from_line(line);
        let flag = if r.underperforming() { "  <- check this turbine" } else { "" };
        println!("{} at {:>4} m/s: {:>6.0} kW of {:>6.0} expected{flag}", r.turbine, r.wind_ms, r.power_kw, r.expected_kw());
    }
}
