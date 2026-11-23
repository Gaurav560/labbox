use ch15_errors::*;

#[test]
fn labbox_checks() {
    task("number", || {
        if number(" 12.4 ", "wind speed") != Ok(12.4) {
            return Err(differs("A good field gives Ok(the number), trimmed.", Ok::<f64, String>(12.4), number(" 12.4 ", "wind speed")));
        }
        let got = number("windy", "wind speed");
        if got != Err("wind speed is not a number: \"windy\"".to_string()) {
            return Err(differs("A bad field gives Err(format!(\"{what} is not a number: {field:?}\")).", "Err(\"wind speed is not a number: \\\"windy\\\"\")", got));
        }
        Ok("Ok with the value, or Err with a message a person can act on.".into())
    });
    task("parse_reading", || {
        let got = parse_reading("T07,10:10,12.4,2100");
        if got != Ok(Reading { turbine: "T07".into(), wind_ms: 12.4, power_kw: 2100.0 }) {
            return Err(differs("A good line gives Ok(Reading { ... }).", "Ok(Reading { turbine: T07, wind_ms: 12.4, power_kw: 2100.0 })", got));
        }
        for (line, want) in [("T07,10:20,12.9", "expected 4 fields, found 3"), ("T07,10:30,windy,2180", "wind speed is not a number: \"windy\""),
                             ("T07,10:50,13.4,22O0", "power is not a number: \"22O0\"")] {
            let got = parse_reading(line);
            if got != Err(want.to_string()) {
                return Err(differs(&format!("parse_reading({line:?}): pass number()'s error up with ?."), want, got));
            }
        }
        Ok("? passed each error up the moment it happened: no unwrap, no panic.".into())
    });
}
