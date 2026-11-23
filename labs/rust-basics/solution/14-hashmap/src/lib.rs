//! Chapter 14: maps and sets.
use std::collections::{HashMap, HashSet};

/// Energy made by each turbine, in kWh, from log lines "T07,time,wind,kW" (one every ten minutes).
/// Broken lines are skipped.
pub fn energy_by_turbine(lines: &[&str]) -> HashMap<String, f64> {
    let mut energy: HashMap<String, f64> = HashMap::new();
    for line in lines {
        let parts: Vec<&str> = line.split(',').collect();
        let [turbine, _, _, kw] = parts[..] else { continue };
        let Ok(kw) = kw.trim().parse::<f64>() else { continue };
        *energy.entry(turbine.to_string()).or_insert(0.0) += kw * 10.0 / 60.0;
    }
    energy
}

/// The turbines of the farm that sent no reading at all, sorted: they may have lost power or their radio.
pub fn silent_turbines(farm: &[&str], reported: &[&str]) -> Vec<String> {
    let heard: HashSet<&str> = reported.iter().copied().collect();
    let mut silent = Vec::new();
    for id in farm {
        if !heard.contains(id) {
            silent.push(id.to_string());
        }
    }
    silent.sort();
    silent
}
