use ch13_vec_and_string::*;

#[test]
fn labbox_checks() {
    task("moving_average", || {
        let got = moving_average(&[10.0, 20.0, 30.0, 40.0], 2);
        if got != vec![15.0, 25.0, 35.0] {
            return Err(differs("Average each window of 2: [10, 20] gives 15, [20, 30] gives 25, ...", vec![15.0, 25.0, 35.0], got));
        }
        let got = moving_average(&[2100.0, 2180.0, 2490.0], 3);
        if got.len() != 1 || !close(got[0], 2256.667) {
            return Err(differs("One window of 3 readings gives one average.", "[2256.67]", got));
        }
        if !moving_average(&[1.0], 3).is_empty() {
            return Err(fail("Fewer readings than the window give an empty Vec (windows() yields nothing)."));
        }
        Ok("A sliding window over the log, each average pushed onto a new Vec.".into())
    });
    task("as_sentence", || {
        let cases: [(&[&str], &str); 4] = [(&[], "no turbines"), (&["T07"], "T07"), (&["T07", "T12"], "T07 and T12"),
                                          (&["T07", "T12", "T31", "T40"], "T07, T12, T31 and T40")];
        for (ids, want) in cases {
            let got = as_sentence(ids);
            if got != want {
                return Err(differs(&format!("as_sentence({ids:?})"), want, got));
            }
        }
        Ok("Commas between, \"and\" before the last: a String built piece by piece.".into())
    });
}
