// Chapter 26: run it with  cargo run
use std::time::{Duration, Instant};

use ch26_async::{poll, poll_all, poll_with_timeout};

#[tokio::main]
async fn main() {
    let ids: Vec<String> = (1..=40).filter(|n| *n != 31).map(|n| format!("T{n:02}")).collect();
    let ids: Vec<&str> = ids.iter().map(|s| s.as_str()).collect();

    let start = Instant::now();
    for id in &ids[..10] {
        poll(id.to_string()).await;
    }
    println!("10 turbines one after another: {:.2} s", start.elapsed().as_secs_f64());

    let start = Instant::now();
    let answers = poll_all(&ids).await;
    println!("{} turbines at once: {:.2} s, first {:?}", answers.len(), start.elapsed().as_secs_f64(), answers[0]);

    for id in ["T07", "T31"] {
        let start = Instant::now();
        let answer = poll_with_timeout(id, Duration::from_millis(500)).await;
        println!("{id}: {answer:?} after {:.2} s", start.elapsed().as_secs_f64());
    }
}
