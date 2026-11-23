use ch20_closures::*;

#[test]
fn labbox_checks() {
    task("below", || {
        let rule = below(200.0);
        let cases = [(7.5, 140.0, true), (7.5, 250.0, false), (5.0, 50.0, false), (12.0, 199.9, true)];
        for (wind, kw, want) in cases {
            if rule(&Reading::new("T", wind, kw)) != want {
                return Err(differs(&format!("below(200.0) for {kw} kW at {wind} m/s: wind >= 6.0 and power below the limit."), want, !want));
            }
        }
        let tight = below(100.0);
        if tight(&Reading::new("T", 7.5, 140.0)) {
            return Err(fail("Each rule must keep its own limit: capture limit_kw with move."));
        }
        Ok("A function that returns a function: each rule remembers its own limit.".into())
    });
    task("alerts", || {
        let readings = vec![Reading::new("T07", 12.4, 2100.0), Reading::new("T12", 7.5, 140.0)];
        let rules: Vec<(&str, Box<dyn Fn(&Reading) -> bool>)> = vec![
            ("low power", Box::new(|r: &Reading| r.power_kw < 200.0)),
            ("windy", Box::new(|r: &Reading| r.wind_ms > 7.0)),
        ];
        let got = alerts(&readings, &rules);
        let want = vec!["T07: windy".to_string(), "T12: low power".to_string(), "T12: windy".to_string()];
        if got != want {
            return Err(differs("For each reading, each rule in order: push \"turbine: rule name\" when it is true.", &want, &got));
        }
        Ok("Rules as data: a list of boxed closures, called like functions.".into())
    });
}
