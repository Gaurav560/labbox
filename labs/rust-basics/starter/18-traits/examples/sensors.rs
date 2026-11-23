// Chapter 18: an example program. Run it with  cargo run --example sensors
use ch18_traits::{report, Anemometer, PowerMeter, Reading, Sensor};

fn main() {
    let r = Reading::new("T07", 12.43, 2100.0);
    println!("{r}");
    println!("{r:?}");

    let sensors: Vec<Box<dyn Sensor>> = vec![
        Box::new(Anemometer { turbine: "T07".into(), wind_ms: 12.43 }),
        Box::new(PowerMeter { turbine: "T07".into(), kw: 2100.0 }),
        Box::new(Anemometer { turbine: "T12".into(), wind_ms: 7.5 }),
    ];
    for line in report(&sensors) {
        println!("{line}");
    }
}
