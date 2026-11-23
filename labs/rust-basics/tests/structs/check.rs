use ch09_structs::*;

#[test]
fn labbox_checks() {
    task("from_line", || {
        let got = Reading::from_line("T07,2026-11-24 10:10,12.4,2100");
        let want = Reading { turbine: "T07".into(), time: "2026-11-24 10:10".into(), wind_ms: 12.4, power_kw: 2100.0 };
        if got != want {
            return Err(differs("Set every field from the line's four parts.", &want, &got));
        }
        let got = Reading::from_line("T31,2026-11-24 10:10, 25.6 , 0");
        if !close(got.wind_ms, 25.6) || got.power_kw != 0.0 {
            return Err(differs("Trim the numbers before parsing them.", "25.6 m/s, 0 kW", (got.wind_ms, got.power_kw)));
        }
        Ok("A line became one Reading with four named fields.".into())
    });
    task("underperforming", || {
        let r = |wind: f64, kw: f64| Reading { turbine: "T".into(), time: "t".into(), wind_ms: wind, power_kw: kw };
        let cases = [(7.5, 140.0, true), (7.5, 305.0, false), (14.0, 1900.0, true), (14.0, 2100.0, false), (2.0, 0.0, false), (26.0, 0.0, false)];
        for (wind, kw, want) in cases {
            let got = r(wind, kw).underperforming();
            if got != want {
                return Err(differs(&format!("At {wind} m/s and {kw} kW: true only when expected > 0 and power < 80% of expected."), want, got));
            }
        }
        Ok("A method that reads its own fields through &self and calls another method.".into())
    });
}
