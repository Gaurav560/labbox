//! The farm's summary over many log lines.
use crate::reading::parse_line;

/// What the control room sees at the top of the screen.
#[derive(Debug, PartialEq)]
pub struct Summary {
    pub turbines: usize,
    pub readings: usize,
    pub skipped: usize,
    pub energy_mwh: f64,
}

/// Summarises log lines (one reading every ten minutes per turbine). Broken lines are counted, not used.
pub fn farm_summary(lines: &[&str]) -> Summary {
    let mut turbines: Vec<String> = Vec::new();
    let mut readings = 0;
    let mut skipped = 0;
    let mut energy_kwh = 0.0;
    for line in lines {
        match parse_line(line) {
            Some(r) => {
                readings += 1;
                energy_kwh += r.power_kw * 10.0 / 60.0;
                if !turbines.contains(&r.turbine) {
                    turbines.push(r.turbine);
                }
            }
            None => skipped += 1,
        }
    }
    Summary { turbines: turbines.len(), readings, skipped, energy_mwh: energy_kwh / 1_000.0 }
}
