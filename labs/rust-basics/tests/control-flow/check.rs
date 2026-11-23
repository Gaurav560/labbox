use ch05_control_flow::*;

#[test]
fn labbox_checks() {
    task("status", || {
        for (wind, want) in [(0.0, "too calm"), (2.99, "too calm"), (3.0, "generating"), (24.9, "generating"), (25.0, "storm stop"), (40.0, "storm stop")] {
            let got = status(wind);
            if got != want {
                return Err(differs(&format!("status({wind}) should be {want:?}. Watch the edges: 3.0 generates, 25.0 stops."), want, got));
            }
        }
        Ok("Three answers from one if / else if / else expression, edges included.".into())
    });
    task("hours_generating", || {
        let mut day = [10.0; 24];
        if hours_generating(day) != 24 {
            return Err(differs("A day of steady 10 m/s wind generates in all 24 hours.", 24, hours_generating(day)));
        }
        day[0] = 1.0;
        day[5] = 2.9;
        day[18] = 26.0;
        let got = hours_generating(day);
        if got != 21 {
            return Err(differs("Count only the hours where status(wind) is \"generating\".", 21, got));
        }
        Ok("A for loop over the day's 24 readings, and a mutable counter.".into())
    });
}
