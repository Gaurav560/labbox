//! Chapter 25: threads. Many turbines at once, safely.
use std::sync::mpsc;
use std::thread;

/// The sum of each log, every log on its own thread, results in the same order as the logs.
pub fn parallel_totals(logs: &[Vec<f64>]) -> Vec<f64> {
    thread::scope(|s| {
        let handles: Vec<_> = logs.iter().map(|log| s.spawn(move || log.iter().sum::<f64>())).collect();
        handles.into_iter().map(|h| h.join().unwrap()).collect()
    })
}

/// One alert per turbine with readings below `low_kw`, like "T12: 3 low readings", sent back over a channel by
/// each turbine's thread, sorted.
pub fn collect_alerts(logs: &[(String, Vec<f64>)], low_kw: f64) -> Vec<String> {
    let (tx, rx) = mpsc::channel();
    thread::scope(|s| {
        for (id, log) in logs {
            let tx = tx.clone();
            s.spawn(move || {
                let low = log.iter().filter(|&&kw| kw < low_kw).count();
                if low > 0 {
                    tx.send(format!("{id}: {low} low readings")).unwrap();
                }
            });
        }
    });
    drop(tx);
    let mut alerts: Vec<String> = rx.iter().collect();
    alerts.sort();
    alerts
}
