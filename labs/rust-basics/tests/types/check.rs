use ch03_types::*;

#[test]
fn labbox_checks() {
    task("energy_kwh", || {
        for (p, m, want) in [(2100, 10, 350.0), (2500, 1440, 60000.0), (40, 45, 30.0)] {
            let got = energy_kwh(p, m);
            if !close(got, want) {
                return Err(differs(&format!("energy_kwh({p}, {m}) should be {want}: power * minutes / 60, in f64."), want, got));
            }
        }
        Ok("u32 to f64 with `as`, then floating-point maths: 2100 kW for 10 minutes is 350 kWh.".into())
    });
    task("describe", || {
        let got = describe((7, 12.43, 2100));
        if got != "T07: 12.4 m/s, 2100 kW" {
            return Err(differs("Use format!(\"T{turbine:02}: {wind:.1} m/s, {power} kW\").", "T07: 12.4 m/s, 2100 kW", got));
        }
        let got = describe((31, 24.96, 2500));
        if got != "T31: 25.0 m/s, 2500 kW" {
            return Err(differs("Round the wind to one decimal with {wind:.1}.", "T31: 25.0 m/s, 2500 kW", got));
        }
        Ok("A tuple taken apart into three names, and formatted with padding and rounding.".into())
    });
}
