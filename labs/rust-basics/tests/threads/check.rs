use ch25_threads::*;

#[test]
fn labbox_checks() {
    task("scoped_threads", || {
        let logs: Vec<Vec<f64>> = (0..12).map(|t| (0..1000).map(|i| (i + t) as f64).collect()).collect();
        let want: Vec<f64> = logs.iter().map(|l| l.iter().sum()).collect();
        let got = parallel_totals(&logs);
        if got != want {
            return Err(differs("One sum per log, in the logs' order (join the handles in order).", &want[..3], got.get(..3)));
        }
        Ok("Twelve threads, borrowed logs, and the answers in order.".into())
    });
    task("channel_alerts", || {
        let logs = vec![("T07".to_string(), vec![2100.0, 2180.0]), ("T12".to_string(), vec![140.0, 165.0, 90.0]),
                        ("T19".to_string(), vec![305.0, 150.0])];
        let got = collect_alerts(&logs, 200.0);
        if got != vec!["T12: 3 low readings".to_string(), "T19: 1 low readings".to_string()] {
            return Err(differs("Each turbine's thread sends an alert when it has low readings.", ["T12: 3 low readings", "T19: 1 low readings"], got));
        }
        Ok("Many senders, one receiver: the threads talked over a channel.".into())
    });
}
