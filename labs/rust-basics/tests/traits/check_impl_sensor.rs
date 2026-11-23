use ch18_traits::*;

#[test]
fn labbox_checks() {
    task("impl_sensor", || {
        let m = PowerMeter { turbine: "T07".into(), kw: 2100.0 };
        if m.describe() != "T07 power meter reads 2100.0 kW" {
            return Err(differs("id, value and unit for a PowerMeter; describe() comes from the trait's default.", "T07 power meter reads 2100.0 kW", m.describe()));
        }
        let sensors: Vec<Box<dyn Sensor>> = vec![Box::new(Anemometer { turbine: "T12".into(), wind_ms: 7.5 }), Box::new(m)];
        let got = report(&sensors);
        if got != vec!["T12 anemometer reads 7.5 m/s".to_string(), "T07 power meter reads 2100.0 kW".to_string()] {
            return Err(differs("report() should describe both kinds of sensor.", "two lines", got));
        }
        Ok("Two different types, one trait, in one Vec<Box<dyn Sensor>>.".into())
    });
}
