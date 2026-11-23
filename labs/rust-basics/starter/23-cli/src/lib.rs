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

    // TODO (task cli_args): these two are meant to be options, written --turbine T07 and --low-kw 150. Without
    //   `long`, clap reads them as more positional arguments (windwatch farm.csv T07 150). Add  #[arg(long)]  above
    //   turbine, and change low_kw's line to  #[arg(long, default_value_t = 200.0)]. Doc comments become --help.
    /// Only this turbine, like T07
    pub turbine: Option<String>,

    /// Flag readings below this power (kW) while the wind is 6 m/s or more
    #[arg(default_value_t = 200.0)]
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
    // TODO (task read_csv): open the file with csv::Reader::from_path(path), adding
    //   .with_context(|| format!("cannot open {}", path.display()))?. Then for row in reader.deserialize(), turn
    //   each row into a Reading with  let reading: Reading = row.with_context(|| format!("bad row in {}",
    //   path.display()))?;  and push it. Return Ok(readings).
    let _ = path;
    todo!()
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
