// Chapter 27: run it with  cargo run --release   (and compare: python3 compare.py)
use std::fs;
use std::time::Instant;

use ch27_speed::energy_by_turbine;

fn main() -> std::io::Result<()> {
    let path = "data/quarter.log";
    if fs::metadata(path).is_err() {
        // 40 turbines, 90 days, a reading every ten minutes: 518,400 lines
        let mut text = String::new();
        for i in 0..90 * 144 {
            for t in 1..=40 {
                text.push_str(&format!("T{t:02},2026-08-{:02} {:02}:{:02}0,{:.1},{}\n", 1 + i / 144 % 28, i % 144 / 6, i % 6,
                                       ((i * 7 + t * 13) % 280) as f64 / 10.0, (i * 31 + t * 17) % 2501));
            }
        }
        fs::create_dir_all("data")?;
        fs::write(path, text)?;
    }
    let start = Instant::now();
    let text = fs::read_to_string(path)?;
    let totals = energy_by_turbine(&text);
    let elapsed = start.elapsed();
    let lines = text.lines().count();
    println!("{lines} lines, {} MB, {} turbines", text.len() / 1_000_000, totals.len());
    println!("T07: {:.0} kWh", totals.get("T07").copied().unwrap_or(0.0));
    println!("read and totalled in {:.1} ms", elapsed.as_secs_f64() * 1000.0);
    Ok(())
}
