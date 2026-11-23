use ch17_generics::*;

#[test]
fn labbox_checks() {
    task("largest", || {
        let got = (largest(&[2100.0, 2490.0, 1650.0]), largest(&[204_u16, 512, 87]), largest(&['a', 'q', 'm']), largest::<f64>(&[]));
        if got != (Some(2490.0), Some(512), Some('q'), None) {
            return Err(differs("The largest item for any type T, or None for an empty list.", (Some(2490.0), Some(512), Some('q'), None::<f64>), got));
        }
        Ok("One function, checked once, working for f64, u16 and char.".into())
    });
    task("series_peak", || {
        let mut s: Series<u16> = Series::new("faults");
        if s.peak().is_some() {
            return Err(fail("An empty series has no peak: None."));
        }
        s.push(204);
        s.push(512);
        s.push(87);
        if s.peak() != Some(512) {
            return Err(differs("peak() should call largest(&self.values).", Some(512), s.peak()));
        }
        Ok("A generic struct's method reused the generic function: no copy of the logic.".into())
    });
}
