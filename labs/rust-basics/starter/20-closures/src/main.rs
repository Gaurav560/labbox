// Chapter 20: run it with  cargo run
use ch20_closures::{alerts, below, Reading};

fn main() {
    let readings = vec![
        Reading::new("T07", 12.4, 2100.0),
        Reading::new("T12", 7.5, 140.0),
        Reading::new("T19", 26.0, 0.0),
        Reading::new("T31", 2.0, 0.0),
    ];

    let storm_limit = 25.0;
    let rules: Vec<(&str, Box<dyn Fn(&Reading) -> bool>)> = vec![
        ("low power", Box::new(below(200.0))),
        ("storm stop", Box::new(move |r: &Reading| r.wind_ms >= storm_limit)),
        ("idle in good wind", Box::new(|r: &Reading| r.wind_ms >= 6.0 && r.power_kw == 0.0)),
    ];
    for line in alerts(&readings, &rules) {
        println!("{line}");
    }

    let mut by_power = readings.clone();
    by_power.sort_by(|a, b| b.power_kw.total_cmp(&a.power_kw));
    let order: Vec<&str> = by_power.iter().map(|r| r.turbine.as_str()).collect();
    println!("by power: {order:?}");

    let mut checks = 0;
    let mut count = |r: &Reading| {
        checks += 1;
        r.power_kw > 0.0
    };
    let running = readings.iter().filter(|r| count(r)).count();
    println!("{running} running, {checks} checks");
}
