//! Chapter 13: vectors and strings in depth.

/// The average of every `window` readings in a row, sliding one reading at a time. Smooths out gusts.
/// [10, 20, 30, 40] with a window of 2 gives [15, 25, 35].
pub fn moving_average(log: &[f64], window: usize) -> Vec<f64> {
    // TODO (task moving_average): make an empty Vec, then for each group in log.windows(window) (a slice of
    //   `window` readings in a row), add up the group, push total / window as f64, and return the Vec.
    todo!()
}

/// A list of turbine ids as a sentence: ["T07"] is "T07", ["T07", "T12"] is "T07 and T12",
/// ["T07", "T12", "T31"] is "T07, T12 and T31", and an empty list is "no turbines".
pub fn as_sentence(ids: &[&str]) -> String {
    match ids {
        [] => "no turbines".to_string(),
        [only] => only.to_string(),
        [rest @ .., last] => {
            // TODO (task as_sentence): build a String: push each id of `rest` with ", " between them
            //   (for (i, id) in rest.iter().enumerate(), and only add ", " when i > 0), then push " and " and last.
            todo!()
        }
    }
}
