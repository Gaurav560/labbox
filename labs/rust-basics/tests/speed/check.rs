use ch27_speed::*;

#[test]
fn labbox_checks() {
    task("fast_parse", || {
        let line = String::from("T07,2026-11-24 10:10,12.4,2100");
        let got = turbine_and_power(&line);
        if got != Some(("T07", 2100.0)) {
            return Err(differs("The first field and the last field as a number.", Some(("T07", 2100.0)), got));
        }
        if got.unwrap().0.as_ptr() != line.as_ptr() {
            return Err(fail("The turbine must be a slice of the line, not a copy."));
        }
        if turbine_and_power("T07").is_some() || turbine_and_power("T07,x,1,22O0").is_some() {
            return Err(fail("No comma, or a power that is not a number, gives None."));
        }
        Ok("Two splits and one parse: nothing copied.".into())
    });
    task("borrowed_keys", || {
        let text = String::from("T07,a,12,2100\nT12,a,7,140\nT07,b,13,2180\nbroken\n");
        let got = energy_by_turbine(&text);
        let t07 = got.get("T07").copied().unwrap_or(0.0);
        if got.len() != 2 || !close(t07, 713.333) {
            return Err(differs("Each turbine's kWh, with &str keys taken from the text.", "2 turbines, T07: 713.3", format!("{} turbines, T07: {t07:.1}", got.len())));
        }
        let key = got.keys().find(|k| **k == "T07").unwrap();
        let start = text.as_ptr() as usize;
        if !(start..start + text.len()).contains(&(key.as_ptr() as usize)) {
            return Err(fail("The keys should point into the text (entry(turbine) with the slice), not be new Strings."));
        }
        Ok("A map whose keys are views into the file's text: no String per line.".into())
    });
}
