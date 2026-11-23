use ch23_cli::*;
use clap::Parser;

#[test]
fn labbox_checks() {
    task("cli_args", || {
        let args = Args::try_parse_from(["windwatch", "farm.csv", "--turbine", "T07", "--low-kw", "150"])
            .map_err(|e| format!("clap refused `windwatch farm.csv --turbine T07 --low-kw 150`: {}", e.to_string().lines().next().unwrap_or("")))?;
        if args.turbine.as_deref() != Some("T07") || args.low_kw != 150.0 {
            return Err(differs("--turbine and --low-kw should fill the two fields.", "turbine Some(\"T07\"), low_kw 150", format!("{:?}, {}", args.turbine, args.low_kw)));
        }
        let plain = Args::try_parse_from(["windwatch", "farm.csv"]).map_err(|_| "with only a file, --turbine and --low-kw must be optional".to_string())?;
        if plain.turbine.is_some() || plain.low_kw != 200.0 {
            return Err(differs("Without options: no turbine, and low_kw defaults to 200.", "None, 200", format!("{:?}, {}", plain.turbine, plain.low_kw)));
        }
        Ok("Two options with --names, one with a default: clap wrote the parsing and the --help.".into())
    });
    task("read_csv", || {
        let dir = std::env::temp_dir();
        let good = dir.join("labbox_farm.csv");
        let bad = dir.join("labbox_broken.csv");
        std::fs::write(&good, "turbine,time,wind_ms,power_kw\nT07,10:10,12.4,2100\nT12,10:10,7.5,140\n").unwrap();
        std::fs::write(&bad, "turbine,time,wind_ms,power_kw\nT07,10:20,12.9,22O0\n").unwrap();
        let rows = read_readings(&good).map_err(|e| format!("{e:#}"))?;
        let want = vec![Reading { turbine: "T07".into(), time: "10:10".into(), wind_ms: 12.4, power_kw: 2100.0 },
                        Reading { turbine: "T12".into(), time: "10:10".into(), wind_ms: 7.5, power_kw: 140.0 }];
        if rows != want {
            return Err(differs("Every row, deserialized into a Reading.", &want, &rows));
        }
        let err = format!("{:#}", read_readings(&bad).expect_err("22O0 is not a number"));
        if !err.contains("bad row in") {
            return Err(differs("A broken row should say: bad row in <file>, then the cause.", "bad row in .../labbox_broken.csv: ...", err));
        }
        let err = format!("{:#}", read_readings(std::path::Path::new("/nowhere/farm.csv")).expect_err("missing file"));
        if !err.contains("cannot open /nowhere/farm.csv") {
            return Err(differs("A missing file should say: cannot open <file>.", "cannot open /nowhere/farm.csv: ...", err));
        }
        Ok("csv read each row and serde filled a Reading by the header's names.".into())
    });
}
