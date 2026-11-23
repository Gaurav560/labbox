use ch26_async::*;
use std::time::{Duration, Instant};

#[test]
fn labbox_checks() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    task("concurrent_poll", || {
        let ids: Vec<String> = (1..=20).map(|n| format!("T{n:02}")).collect();
        let ids: Vec<&str> = ids.iter().map(|s| s.as_str()).collect();
        let start = Instant::now();
        let answers = rt.block_on(poll_all(&ids));
        let took = start.elapsed();
        if answers.len() != 20 || answers[0].0 != "T01" || answers[19].0 != "T20" {
            return Err(fail("Every turbine's answer, sorted by id."));
        }
        if took > Duration::from_millis(1000) {
            return Err(differs("Ask them all at once with a JoinSet: 20 turbines should take about 0.15 s, not one after another.", "under 1 s", format!("{:.2} s", took.as_secs_f64())));
        }
        Ok(format!("20 radios answered in {:.2} s, all waiting at the same time.", took.as_secs_f64()))
    });
    task("with_timeout", || {
        let start = Instant::now();
        let slow = rt.block_on(poll_with_timeout("T31", Duration::from_millis(300)));
        let took = start.elapsed();
        if slow != Err("T31 did not answer in 300 ms".to_string()) || took > Duration::from_millis(1000) {
            return Err(differs("T31 takes 3 s: give up after the limit with Err(\"T31 did not answer in 300 ms\").", "Err after 0.3 s", format!("{slow:?} after {:.1} s", took.as_secs_f64())));
        }
        if rt.block_on(poll_with_timeout("T07", Duration::from_secs(1))).is_err() {
            return Err(fail("A turbine that answers in time gives Ok."));
        }
        Ok("The slow radio was given up on after 0.3 s, and the program moved on.".into())
    });
}
