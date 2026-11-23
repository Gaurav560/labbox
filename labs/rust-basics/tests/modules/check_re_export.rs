use ch12_modules::farm_summary;

#[test]
fn labbox_checks() {
    task("re_export", || {
        let got = farm_summary(&["T31,a,25.6,0"]);
        if got.readings != 1 || got.turbines != 1 {
            return Err(fail("farm_summary is reachable, but did not summarise one line correctly."));
        }
        Ok("pub use made ch12_modules::farm_summary a short path to the same function.".into())
    });
}
