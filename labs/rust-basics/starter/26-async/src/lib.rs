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
    // TODO (task concurrent_poll): this asks one turbine after another. Ask them all at once instead: make a
    //   JoinSet::new(), set.spawn(poll(id.to_string())) for each id, then
    //   while let Some(answer) = set.join_next().await { answers.push(answer.unwrap()); }  and sort by id.
    let mut answers = Vec::new();
    for id in ids {
        answers.push(poll(id.to_string()).await);
    }
    let _ = JoinSet::<()>::new;
    answers
}

/// One turbine, but give up after `limit`.
pub async fn poll_with_timeout(id: &str, limit: Duration) -> Result<(String, f64), String> {
    // TODO (task with_timeout): wrap the poll in timeout(limit, poll(id.to_string())).await. Ok(answer) gives
    //   Ok(answer); Err(_) gives Err(format!("{id} did not answer in {} ms", limit.as_millis())).
    let _ = timeout::<std::future::Ready<()>>;
    Ok(poll(id.to_string()).await).map(|a| { let _ = limit; a })
}
