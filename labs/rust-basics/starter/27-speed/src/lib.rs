//! Chapter 27: speed. Parsing a quarter of a year of logs, without copying a single field.
use std::collections::HashMap;

/// "T07,2026-11-24 10:10,12.4,2100" gives Some(("T07", 2100.0)): the turbine is a slice of the line.
pub fn turbine_and_power(line: &str) -> Option<(&str, f64)> {
    // TODO (task fast_parse): split at the first comma with  let (turbine, rest) = line.split_once(',')?;  then
    //   take the last field with  let (_, power) = rest.rsplit_once(',')?;  and return
    //   Some((turbine, power.trim().parse().ok()?)).
    let _ = line;
    todo!()
}

/// Energy per turbine in kWh (ten minutes a reading). The keys borrow from the text: no String per line.
pub fn energy_by_turbine(text: &str) -> HashMap<&str, f64> {
    // TODO (task borrowed_keys): for each line in text.lines(), if let Some((turbine, kw)) = turbine_and_power(line),
    //   add kw * 10.0 / 60.0 to *totals.entry(turbine).or_insert(0.0). The key is a &str slice of the text.
    let totals = HashMap::new();
    let _ = text;
    totals
}
