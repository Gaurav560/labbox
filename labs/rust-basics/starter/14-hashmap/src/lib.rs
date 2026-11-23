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
        // TODO (task energy_by_turbine): add kw * 10.0 / 60.0 to this turbine's total. entry() finds the
        //   turbine's place in the map, or_insert(0.0) creates it at 0.0 the first time, and * reaches the number:
        //   *energy.entry(turbine.to_string()).or_insert(0.0) += kw * 10.0 / 60.0;
        let _ = (turbine, kw);
    }
    energy
}

/// The turbines of the farm that sent no reading at all, sorted: they may have lost power or their radio.
pub fn silent_turbines(farm: &[&str], reported: &[&str]) -> Vec<String> {
    let heard: HashSet<&str> = reported.iter().copied().collect();
    // TODO (task silent_turbines): for each id in farm that heard does not contain (!heard.contains(id)), push
    //   id.to_string() onto a Vec; sort it and return it.
    let _ = heard;
    todo!()
}
