use ch14_hashmap::*;

#[test]
fn labbox_checks() {
    task("energy_by_turbine", || {
        let got = energy_by_turbine(&["T07,a,12.4,2100", "T12,a,7.5,140", "T07,b,12.9,2180", "T31,a,13.0,x", "broken"]);
        let t07 = got.get("T07").copied().unwrap_or(0.0);
        let t12 = got.get("T12").copied().unwrap_or(0.0);
        if !close(t07, 713.333) || !close(t12, 23.333) {
            return Err(differs("Each turbine's kWh: add kw * 10 / 60 into its entry.", "T07: 713.3, T12: 23.3", format!("T07: {t07:.1}, T12: {t12:.1}")));
        }
        if got.len() != 2 {
            return Err(differs("Only turbines with a good reading appear.", 2, got.len()));
        }
        Ok("entry().or_insert(0.0) made each turbine's total on its first reading and added to it after.".into())
    });
    task("silent_turbines", || {
        let got = silent_turbines(&["T01", "T02", "T03", "T04"], &["T03", "T01", "T03"]);
        if got != vec!["T02".to_string(), "T04".to_string()] {
            return Err(differs("The farm's turbines that are not in the set of reported ones, sorted.", ["T02", "T04"], got));
        }
        if !silent_turbines(&["T01"], &["T01"]).is_empty() {
            return Err(fail("When every turbine reported, the list is empty."));
        }
        Ok("A HashSet answered \"did we hear from it?\" in one step for each turbine.".into())
    });
}
