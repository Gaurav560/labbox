use ch10_enums::*;

#[test]
fn labbox_checks() {
    task("classify", || {
        let cases = [((12.4, 2100.0, None), Status::Generating { kw: 2100.0 }), ((2.1, 0.0, None), Status::Calm),
                     ((25.0, 0.0, None), Status::StormStop), ((14.0, 0.0, Some(512)), Status::Fault(512)),
                     ((1.0, 0.0, Some(7)), Status::Fault(7))];
        for ((wind, kw, fault), want) in cases {
            let got = classify(wind, kw, fault);
            if got != want {
                return Err(differs(&format!("classify({wind}, {kw}, {fault:?}): a fault comes first, then the wind decides."), want, got));
            }
        }
        Ok("Every variant built, one of them carrying its power, one its fault code.".into())
    });
    task("peak_power", || {
        let got = (peak_power(&[2100.0, 2400.0, 2250.0]), peak_power(&[]), peak_power(&[5.0]));
        if got != (Some(2400.0), None, Some(5.0)) {
            return Err(differs("Some(the largest reading), or None for an empty log.", (Some(2400.0), None::<f64>, Some(5.0)), got));
        }
        Ok("No peak of nothing: None says so, and the caller must handle it.".into())
    });
}
