use ch04_functions::*;

#[test]
fn labbox_checks() {
    task("tip_speed", || {
        for (rpm, blade, want) in [(12.0, 50.0, 62.832), (15.5, 50.0, 81.158), (8.0, 40.0, 33.510)] {
            let got = tip_speed(rpm, blade);
            if !close(got, want) {
                return Err(differs(&format!("tip_speed({rpm}, {blade}) should be about {want}: 2 * PI * blade * rpm / 60."), want, got));
            }
        }
        Ok("12 rpm with 50 m blades: the tip moves at 62.8 m/s, about 226 km/h.".into())
    });
    task("capacity_factor", || {
        for (made, want) in [(612.0, 34.0), (1080.0, 60.0), (1800.0, 100.0)] {
            let got = capacity_factor(made, 2500.0, 720.0);
            if !close(got, want) {
                return Err(differs(&format!("capacity_factor({made}, 2500.0, 720.0) should be {want}: made / max_energy_mwh(...) * 100."), want, got));
            }
        }
        Ok("One function calling another: 612 MWh of a possible 1,800 is a 34% capacity factor.".into())
    });
}
