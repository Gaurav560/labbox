// Chapter 21: run it with  cargo run --release   (and once without --release, to compare)
use std::hint::black_box;
use std::time::Instant;

use ch21_iterators::{total_energy_loop, total_energy_mwh, weak_in_strong_wind, Reading};

fn main() {
    let day = vec![Reading::new("T07", 12.4, 2100.0), Reading::new("T12", 13.0, 1450.0),
                   Reading::new("T19", 14.2, 2500.0), Reading::new("T31", 26.0, 0.0)];
    println!("energy: {:.3} MWh", total_energy_mwh(&day));
    println!("weak in strong wind: {:?}", weak_in_strong_wind(&day));

    // A year of 40 turbines, one reading every ten minutes: 2,102,400 readings, made up but realistic.
    let year: Vec<Reading> = (0..40 * 6 * 24 * 365)
        .map(|i| Reading::new("T", 8.0 + (i % 17) as f64, 900.0 + (i % 1601) as f64))
        .collect();
    for (name, f) in [("iterator", total_energy_mwh as fn(&[Reading]) -> f64), ("loop", total_energy_loop)] {
        let start = Instant::now();
        let mut mwh = 0.0;
        for _ in 0..20 {
            mwh = f(black_box(&year));
        }
        println!("{name:>8}: {mwh:.1} MWh, {:.2} ms a pass", start.elapsed().as_secs_f64() * 1000.0 / 20.0);
    }
}
