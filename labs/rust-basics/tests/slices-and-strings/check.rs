use ch08_slices_and_strings::*;

#[test]
fn labbox_checks() {
    task("turbine_id", || {
        for (line, want) in [("T07,2026-11-24 10:10,12.4,2100", "T07"), ("T31,x", "T31"), ("T12", "T12"), (",empty", "")] {
            let got = turbine_id(line);
            if got != want {
                return Err(differs(&format!("turbine_id({line:?}): the text before the first comma, or the whole line."), want, got));
            }
        }
        let line = String::from("T09,a,b,c");
        let id = turbine_id(&line);
        if id.as_ptr() != line.as_ptr() {
            return Err(fail("Return a slice of the line (&line[..comma]), not a new String."));
        }
        Ok("A view into the line itself: no copy, and the compiler knows it lives as long as the line.".into())
    });
    task("last_hour", || {
        let day: Vec<f64> = (1..=10).map(|i| i as f64).collect();
        let got = last_hour(&day);
        if got != &[5.0, 6.0, 7.0, 8.0, 9.0, 10.0][..] {
            return Err(differs("The last 6 readings: &readings[start..] with start = len - 6.", "[5.0, 6.0, 7.0, 8.0, 9.0, 10.0]", format!("{got:?}")));
        }
        let got = last_hour(&day[..3]);
        if got != &[1.0, 2.0, 3.0][..] {
            return Err(differs("With fewer than 6 readings, return them all (saturating_sub stops at 0).", "[1.0, 2.0, 3.0]", format!("{got:?}")));
        }
        Ok("Slices of slices: the last hour, and no panic when there is less than an hour.".into())
    });
}
