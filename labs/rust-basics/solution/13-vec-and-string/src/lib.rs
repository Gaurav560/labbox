//! Chapter 13: vectors and strings in depth.

/// The average of every `window` readings in a row, sliding one reading at a time. Smooths out gusts.
/// [10, 20, 30, 40] with a window of 2 gives [15, 25, 35].
pub fn moving_average(log: &[f64], window: usize) -> Vec<f64> {
    let mut averages = Vec::new();
    for group in log.windows(window) {
        let mut total = 0.0;
        for kw in group {
            total += kw;
        }
        averages.push(total / window as f64);
    }
    averages
}

/// A list of turbine ids as a sentence: ["T07"] is "T07", ["T07", "T12"] is "T07 and T12",
/// ["T07", "T12", "T31"] is "T07, T12 and T31", and an empty list is "no turbines".
pub fn as_sentence(ids: &[&str]) -> String {
    match ids {
        [] => "no turbines".to_string(),
        [only] => only.to_string(),
        [rest @ .., last] => {
            let mut text = String::new();
            for (i, id) in rest.iter().enumerate() {
                if i > 0 {
                    text.push_str(", ");
                }
                text.push_str(id);
            }
            text.push_str(" and ");
            text.push_str(last);
            text
        }
    }
}
