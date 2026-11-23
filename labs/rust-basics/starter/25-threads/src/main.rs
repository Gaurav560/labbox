// Chapter 25: run it with  cargo run --release
use std::thread;
use std::time::Instant;

use ch25_threads::{collect_alerts, parallel_totals};

/// Expected power for a wind speed, worked out the slow, careful way (to give the threads real work).
fn check(log: &[f64]) -> f64 {
    log.iter().map(|w| if *w < 3.0 || *w >= 25.0 { 0.0 } else { 2500.0 * ((w - 3.0) / 9.0).min(1.0).powf(3.0).sqrt().powi(2) }).sum()
}

fn main() {
    println!("this machine has {} CPU threads", thread::available_parallelism().map(|n| n.get()).unwrap_or(1));
    // 40 turbines, a year of wind each (one reading every ten minutes)
    let logs: Vec<Vec<f64>> = (0..40).map(|t| (0..52_560).map(|i| ((i * 7 + t * 13) % 280) as f64 / 10.0).collect()).collect();

    let start = Instant::now();
    let one_by_one: f64 = logs.iter().map(|log| check(log)).sum();
    let alone = start.elapsed();

    let start = Instant::now();
    let together: f64 = thread::scope(|s| {
        let handles: Vec<_> = logs.iter().map(|log| s.spawn(move || check(log))).collect();
        handles.into_iter().map(|h| h.join().unwrap()).sum()
    });
    let threaded = start.elapsed();
    println!("one thread:  {:.0} kW expected in total, {:.1} ms", one_by_one, alone.as_secs_f64() * 1000.0);
    println!("40 threads:  {:.0} kW expected in total, {:.1} ms", together, threaded.as_secs_f64() * 1000.0);

    let totals = parallel_totals(&[vec![2100.0, 2180.0], vec![140.0, 165.0], vec![305.0]]);
    println!("totals: {totals:?}");
    let alerts = collect_alerts(&[("T07".into(), vec![2100.0, 2180.0]), ("T12".into(), vec![140.0, 165.0, 90.0]),
                                  ("T19".into(), vec![305.0, 150.0])], 200.0);
    println!("alerts: {alerts:?}");
}
