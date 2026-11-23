// Chapter 16: run it with  cargo run -- data/t07.log   (or another file)
use ch16_error_types::load;

fn main() -> anyhow::Result<()> {
    let path = std::env::args().nth(1).unwrap_or_else(|| "data/t07.log".to_string());
    let readings = load(&path)?;
    let total: f64 = readings.iter().map(|r| r.power_kw).sum();
    println!("{path}: {} readings, average {:.0} kW", readings.len(), total / readings.len() as f64);
    Ok(())
}
