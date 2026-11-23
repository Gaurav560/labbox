//! Chapter 12: the Windwatch library, split into modules. Each `mod` line below is a file in src/.
pub mod reading; // src/reading.rs: one log line
pub mod report; // src/report.rs: the farm's summary

// Re-exported, so users write ch12_modules::farm_summary instead of ch12_modules::report::farm_summary.
pub use report::farm_summary;

/// One line of text for the control room's screen.
pub fn summary_text(lines: &[&str]) -> String {
    let s = report::farm_summary(lines);
    format!("{} turbines, {} readings ({} skipped), {:.2} MWh", s.turbines, s.readings, s.skipped, s.energy_mwh)
}
