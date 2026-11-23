//! Chapter 23: Windwatch as a command-line tool. Arguments with clap, a CSV log with csv and serde.
use std::path::{Path, PathBuf};

use anyhow::Context;
use clap::Parser;
use serde::Deserialize;

/// Summarise a wind farm's turbine log.
#[derive(Parser, Debug, PartialEq)]
#[command(name = "windwatch", version, about)]
pub struct Args {
    /// The log file: CSV with the header turbine,time,wind_ms,power_kw
    pub file: PathBuf,

    /// Only this turbine, like T07
    #[arg(long)]
    pub turbine: Option<String>,

    /// Flag readings below this power (kW) while the wind is 6 m/s or more
    #[arg(long, default_value_t = 200.0)]
    pub low_kw: f64,
}

/// One row of the CSV log. serde fills the fields by the header's names.
#[derive(Debug, Deserialize, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub time: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

/// Every row of a CSV log, or an error that names the file and the row.
pub fn read_readings(path: &Path) -> anyhow::Result<Vec<Reading>> {
    let mut reader = csv::Reader::from_path(path).with_context(|| format!("cannot open {}", path.display()))?;
    let mut readings = Vec::new();
    for row in reader.deserialize() {
        let reading: Reading = row.with_context(|| format!("bad row in {}", path.display()))?;
        readings.push(reading);
    }
    Ok(readings)
}

/// The report the program prints.
pub fn run(args: &Args) -> anyhow::Result<Vec<String>> {
    let all = read_readings(&args.file)?;
    let chosen: Vec<&Reading> = all.iter().filter(|r| args.turbine.as_deref().is_none_or(|t| r.turbine == t)).collect();
    let mut lines = vec![format!("{} readings", chosen.len())];
    for r in chosen.iter().filter(|r| r.wind_ms >= 6.0 && r.power_kw < args.low_kw) {
        lines.push(format!("low: {} at {}: {} kW in {} m/s", r.turbine, r.time, r.power_kw, r.wind_ms));
    }
    Ok(lines)
}
