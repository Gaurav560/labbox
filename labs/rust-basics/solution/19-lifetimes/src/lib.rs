//! Chapter 19: lifetimes. How long a reference may be used, written where the compiler cannot work it out.

#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

impl Reading {
    pub fn new(turbine: &str, wind_ms: f64, power_kw: f64) -> Reading {
        Reading { turbine: turbine.to_string(), wind_ms, power_kw }
    }
}

/// Of two readings, the one with more power (the first one on a tie). The answer borrows from one of the inputs, so
/// it may be used only while both are alive: that is what 'a says.
pub fn stronger<'a>(a: &'a Reading, b: &'a Reading) -> &'a Reading {
    if b.power_kw > a.power_kw { b } else { a }
}

/// One log line, taken apart without copying: every field borrows from the line.
#[derive(Debug, PartialEq)]
pub struct LogLine<'a> {
    pub turbine: &'a str,
    pub time: &'a str,
    pub wind: &'a str,
    pub power: &'a str,
}

impl<'a> LogLine<'a> {
    /// Splits "T07,2026-11-24 10:10,12.4,2100" into its four fields, or None.
    pub fn parse(line: &'a str) -> Option<LogLine<'a>> {
        let mut fields = line.split(',');
        let turbine = fields.next()?;
        let time = fields.next()?;
        let wind = fields.next()?;
        let power = fields.next()?;
        if fields.next().is_some() {
            return None;
        }
        Some(LogLine { turbine, time, wind, power })
    }
}
