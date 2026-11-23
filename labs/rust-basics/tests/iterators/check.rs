use ch21_iterators::*;

#[test]
fn labbox_checks() {
    task("total_energy", || {
        let day = vec![Reading::new("T07", 12.4, 2100.0), Reading::new("T12", 13.0, 1450.0)];
        let got = total_energy_mwh(&day);
        if !close(got, 0.591667) {
            return Err(differs("Sum power * 10 / 60 over all readings, then / 1000.", 0.5917, got));
        }
        if total_energy_mwh(&[]) != 0.0 {
            return Err(fail("No readings, no energy: 0.0."));
        }
        Ok("map, then sum: one chain, no counter variable.".into())
    });
    task("weak_turbines", || {
        let day = vec![Reading::new("T07", 12.4, 2100.0), Reading::new("T12", 13.0, 1450.0), Reading::new("T19", 11.9, 900.0),
                       Reading::new("T31", 26.0, 0.0), Reading::new("T33", 24.0, 1999.0)];
        let got = weak_in_strong_wind(&day);
        if got != vec!["T12", "T33"] {
            return Err(differs("Winds from 12 to below 25, power below 2000, the ids in order.", vec!["T12", "T33"], got));
        }
        Ok("filter, filter, map, collect: each step says one thing.".into())
    });
}
