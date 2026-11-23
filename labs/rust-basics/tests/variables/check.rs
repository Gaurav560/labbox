use ch02_variables::*;

#[test]
fn labbox_checks() {
    task("capacity_mw", || {
        let got = (capacity_mw(40), capacity_mw(1), capacity_mw(0));
        if got != (100, 2, 0) {
            return Err(differs("capacity_mw(40) should be 100 MW: turbines * RATED_POWER_KW / 1_000.", (100, 2, 0), got));
        }
        Ok("40 turbines of 2,500 kW: 100 MW. The constant did the remembering.".into())
    });
    task("wind_speed", || {
        for (text, want) in [("12.5 m/s", 12.5), ("  3.2m/s ", 3.2), ("25 m/s", 25.0)] {
            let got = wind_speed(text);
            if !close(got, want) {
                return Err(differs(&format!("wind_speed({text:?}) should be {want}: trim, remove \"m/s\", trim, parse."), want, got));
            }
        }
        Ok("Three shadows of one name: text, text without the unit, then a number.".into())
    });
}
