// Chapter 17: run it with  cargo run
use ch17_generics::{largest, Series};

fn main() {
    println!("highest power: {:?}", largest(&[2100.0, 2490.0, 1650.0]));
    println!("highest fault code: {:?}", largest(&[204_u16, 512, 87]));
    println!("latest hour: {:?}", largest(&['a', 'q', 'm']));
    println!("nothing: {:?}", largest::<f64>(&[]));

    let mut power: Series<f64> = Series::new("T07 power, kW");
    for kw in [2100.0, 2180.0, 2490.0] {
        power.push(kw);
    }
    let mut faults: Series<u16> = Series::new("T19 faults");
    faults.push(512);
    faults.push(204);
    println!("{}: peak {:?}", power.name, power.peak());
    println!("{}: peak {:?}", faults.name, faults.peak());
}
