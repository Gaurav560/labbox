use ch12_modules::report::{farm_summary, Summary};

#[test]
fn labbox_checks() {
    task("make_public", || {
        let got = farm_summary(&["T07,a,12.4,2100", "T07,b,12.9,2180", "T12,a,3.1,60", "T12,b,windy,0"]);
        if got.turbines != 2 || got.readings != 3 || got.skipped != 1 || !close(got.energy_mwh, 0.7233) {
            return Err(differs("farm_summary should count 2 turbines, 3 readings and 1 skipped line.",
                               Summary { turbines: 2, readings: 3, skipped: 1, energy_mwh: 0.7233 }, got));
        }
        Ok("pub lets code outside the module call farm_summary.".into())
    });
}
