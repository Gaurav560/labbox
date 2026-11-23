use ch19_lifetimes::*;

#[test]
fn labbox_checks() {
    task("stronger", || {
        let a = Reading::new("T07", 12.4, 2100.0);
        let b = Reading::new("T12", 7.5, 140.0);
        let c = Reading::new("T19", 14.0, 2500.0);
        if stronger(&a, &b).turbine != "T07" || stronger(&a, &c).turbine != "T19" || stronger(&a, &a.clone()).turbine != "T07" {
            return Err(fail("Return the reading with more power (the first one on a tie)."));
        }
        Ok("The signature now says: the answer lives as long as both inputs. It compiles.".into())
    });
    task("zero_copy", || {
        let line = String::from("T07,2026-11-24 10:10,12.4,2100");
        let got = LogLine::parse(&line);
        let want = LogLine { turbine: "T07", time: "2026-11-24 10:10", wind: "12.4", power: "2100" };
        if got.as_ref() != Some(&want) {
            return Err(differs("Four fields taken with fields.next()?", Some(&want), got.as_ref()));
        }
        if got.unwrap().turbine.as_ptr() != line.as_ptr() {
            return Err(fail("Fields must borrow from the line, not copy it."));
        }
        if LogLine::parse("T07,a,b").is_some() || LogLine::parse("a,b,c,d,e").is_some() {
            return Err(fail("Three fields, or five, give None."));
        }
        Ok("Four views into one line: no String was made for any field.".into())
    });
}
