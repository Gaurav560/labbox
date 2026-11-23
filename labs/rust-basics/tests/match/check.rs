use ch11_match::*;

#[test]
fn labbox_checks() {
    task("describe_status", || {
        let cases = [(Status::Generating { kw: 2500.0 }, "full power"), (Status::Generating { kw: 1312.4 }, "generating 1312 kW"),
                     (Status::Fault(512), "fault 512: send the crew now"), (Status::Fault(599), "fault 599: send the crew now"),
                     (Status::Fault(600), "fault 600: check at the next visit"), (Status::Fault(204), "fault 204: check at the next visit"),
                     (Status::Calm, "waiting for wind"), (Status::StormStop, "stopped for the storm")];
        for (status, want) in cases {
            let got = describe(&status);
            if got != want {
                return Err(differs(&format!("describe({status:?})"), want, got));
            }
        }
        Ok("A guard for full power, a range for urgent faults, and every case covered.".into())
    });
    task("parse_line", || {
        let good = parse_line("T07,2026-11-24 10:10,12.4,2100");
        let want = Reading { turbine: "T07".into(), time: "2026-11-24 10:10".into(), wind_ms: 12.4, power_kw: 2100.0 };
        if good.as_ref() != Some(&want) {
            return Err(differs("A good line gives Some(Reading { ... }).", Some(&want), good.as_ref()));
        }
        for bad in ["T07,2026-11-24 10:20,12.9", "T07,x,windy,2180", "T07,x,13.4,22O0", "", "a,b,c,d,e"] {
            if parse_line(bad).is_some() {
                return Err(differs(&format!("parse_line({bad:?}) should be None: let else returns early."), "None", "Some(...)"));
            }
        }
        Ok("Broken lines become None instead of a panic: Windwatch keeps running.".into())
    });
}
