//! Chapter 26: async with Tokio. Waiting for 40 radios at once, on one thread.
use std::time::Duration;

use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};

/// How long a turbine's radio link takes to answer, in ms (made up: T31 is at the far end with a weak signal).
pub fn delay_ms(id: &str) -> u64 {
    if id == "T31" { 3_000 } else { 100 + id.bytes().map(u64::from).sum::<u64>() % 50 }
}

/// Asks one turbine for its power over the radio link (here, a pretend link that just waits).
pub async fn poll(id: String) -> (String, f64) {
    sleep(Duration::from_millis(delay_ms(&id))).await;
    let kw = 1_800.0 + (delay_ms(&id) % 7) as f64 * 100.0;
    (id, kw)
}

/// Asks every turbine at once and returns the answers sorted by id.
pub async fn poll_all(ids: &[&str]) -> Vec<(String, f64)> {
    let mut set = JoinSet::new();
    for id in ids {
        set.spawn(poll(id.to_string()));
    }
    let mut answers = Vec::new();
    while let Some(answer) = set.join_next().await {
        answers.push(answer.unwrap());
    }
    answers.sort_by(|a, b| a.0.cmp(&b.0));
    answers
}

/// One turbine, but give up after `limit`.
pub async fn poll_with_timeout(id: &str, limit: Duration) -> Result<(String, f64), String> {
    match timeout(limit, poll(id.to_string())).await {
        Ok(answer) => Ok(answer),
        Err(_) => Err(format!("{id} did not answer in {} ms", limit.as_millis())),
    }
}
