use ch18_traits::*;

#[test]
fn labbox_checks() {
    task("impl_display", || {
        let got = Reading::new("T07", 12.43, 2100.0).to_string();
        if got != "T07: 12.4 m/s, 2100 kW" {
            return Err(differs("write!(f, \"{}: {:.1} m/s, {:.0} kW\", ...) in fmt.", "T07: 12.4 m/s, 2100 kW", got));
        }
        Ok("Reading now prints for people with {}, and has to_string() for free.".into())
    });
}
