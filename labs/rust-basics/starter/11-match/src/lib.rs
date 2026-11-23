//! Chapter 11: pattern matching with match, if let and let else.

/// One line of a turbine's log, as one value with named fields.
#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub time: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

/// What a turbine is doing (chapter 10).
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Status {
    Calm,
    Generating { kw: f64 },
    StormStop,
    Fault(u16),
}

/// A sentence for the control room. Fault codes 500 to 599 are urgent: they mean the crew must go now.
pub fn describe(status: &Status) -> String {
    match status {
        Status::Calm => "waiting for wind".to_string(),
        Status::StormStop => "stopped for the storm".to_string(),
        // TODO (task describe_status): add the missing arms, in this order:
        //   Status::Generating { kw } if *kw >= 2_500.0  =>  "full power"
        //   Status::Generating { kw }                    =>  format!("generating {kw:.0} kW")
        //   Status::Fault(code @ 500..=599)              =>  format!("fault {code}: send the crew now")
        //   Status::Fault(code)                          =>  format!("fault {code}: check at the next visit")
        _ => todo!(),
    }
}

/// A log line as a Reading, or None if the line is broken (wrong number of fields, or a number that is not one).
pub fn parse_line(line: &str) -> Option<Reading> {
    let parts: Vec<&str> = line.split(',').collect();
    let [turbine, time, wind, power] = parts[..] else {
        return None;
    };
    // TODO (task parse_line): the line has four fields now. Parse wind and power with let else:
    //   let Ok(wind_ms) = wind.trim().parse::<f64>() else { return None; };   (and the same for power_kw), then
    //   return Some(Reading { turbine: turbine.to_string(), time: time.to_string(), wind_ms, power_kw }).
    todo!()
}
