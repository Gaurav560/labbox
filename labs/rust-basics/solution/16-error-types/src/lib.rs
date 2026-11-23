//! Chapter 16: your own error type with thiserror, and anyhow in the program that uses it.
use std::fs;

use anyhow::Context;
use thiserror::Error;

#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

/// Everything that can be wrong with one log line, as values a program can match on.
#[derive(Debug, Error, PartialEq)]
pub enum ReadingError {
    #[error("expected 4 fields, found {found}")]
    FieldCount { found: usize },
    #[error("{field} is not a number: {text:?}")]
    BadNumber { field: &'static str, text: String },
    #[error("power {kw} kW is more than the turbine's 2500 kW")]
    TooMuchPower { kw: f64 },
}

fn number(text: &str, field: &'static str) -> Result<f64, ReadingError> {
    text.trim().parse().map_err(|_| ReadingError::BadNumber { field, text: text.to_string() })
}

/// A log line "T07,time,wind,kW" as a Reading, or the exact ReadingError.
pub fn parse_reading(line: &str) -> Result<Reading, ReadingError> {
    let parts: Vec<&str> = line.split(',').collect();
    if parts.len() != 4 {
        return Err(ReadingError::FieldCount { found: parts.len() });
    }
    let wind_ms = number(parts[2], "wind speed")?;
    let power_kw = number(parts[3], "power")?;
    if power_kw > 2_500.0 {
        return Err(ReadingError::TooMuchPower { kw: power_kw });
    }
    Ok(Reading { turbine: parts[0].to_string(), wind_ms, power_kw })
}

/// Every reading in a log file. Stops at the first problem, saying which file and which line.
pub fn load(path: &str) -> anyhow::Result<Vec<Reading>> {
    let text = fs::read_to_string(path).with_context(|| format!("cannot read {path}"))?;
    let mut readings = Vec::new();
    for (n, line) in text.lines().enumerate() {
        let reading = parse_reading(line).with_context(|| format!("{path}, line {}", n + 1))?;
        readings.push(reading);
    }
    Ok(readings)
}
