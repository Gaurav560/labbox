//! Chapter 9: structs and methods.

/// One turbine's rated power, in kW.
pub const RATED_KW: f64 = 2_500.0;

/// One line of a turbine's log, as one value with named fields.
#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub time: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

impl Reading {
    /// Builds a Reading from a log line like "T07,2026-11-24 10:10,12.4,2100".
    pub fn from_line(line: &str) -> Reading {
        let parts: Vec<&str> = line.split(',').collect();
        // TODO (task from_line): return a Reading { ... } with each field set from parts: turbine and time with
        //   parts[0].to_string() and parts[1].to_string(), wind_ms and power_kw with parts[2].trim().parse().unwrap()
        //   and parts[3].trim().parse().unwrap().
        todo!()
    }

    /// The power a healthy turbine makes at this wind speed (its power curve), in kW.
    pub fn expected_kw(&self) -> f64 {
        if self.wind_ms < 3.0 || self.wind_ms >= 25.0 {
            0.0
        } else if self.wind_ms >= 12.0 {
            RATED_KW
        } else {
            RATED_KW * ((self.wind_ms - 3.0) / 9.0).powi(3)
        }
    }

    /// True when the turbine makes less than 80% of what it should at this wind speed.
    pub fn underperforming(&self) -> bool {
        // TODO (task underperforming): let expected = self.expected_kw(); then return true when expected > 0.0
        //   and self.power_kw < 0.8 * expected.
        todo!()
    }
}
