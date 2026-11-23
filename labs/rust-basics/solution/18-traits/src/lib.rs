//! Chapter 18: traits. Shared behaviour that many types can have.
use std::fmt;

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

/// Printing a Reading for people: "T07: 12.4 m/s, 2100 kW".
impl fmt::Display for Reading {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}: {:.1} m/s, {:.0} kW", self.turbine, self.wind_ms, self.power_kw)
    }
}

/// Anything on a turbine that Windwatch can read.
pub trait Sensor {
    fn id(&self) -> String;
    fn value(&self) -> f64;
    fn unit(&self) -> &'static str;

    /// A default method: every sensor gets it for free, and may replace it.
    fn describe(&self) -> String {
        format!("{} reads {:.1} {}", self.id(), self.value(), self.unit())
    }
}

pub struct Anemometer {
    pub turbine: String,
    pub wind_ms: f64,
}

impl Sensor for Anemometer {
    fn id(&self) -> String {
        format!("{} anemometer", self.turbine)
    }
    fn value(&self) -> f64 {
        self.wind_ms
    }
    fn unit(&self) -> &'static str {
        "m/s"
    }
}

pub struct PowerMeter {
    pub turbine: String,
    pub kw: f64,
}

impl Sensor for PowerMeter {
    fn id(&self) -> String {
        format!("{} power meter", self.turbine)
    }
    fn value(&self) -> f64 {
        self.kw
    }
    fn unit(&self) -> &'static str {
        "kW"
    }
}

/// One line per sensor, whatever kind each one is.
pub fn report(sensors: &[Box<dyn Sensor>]) -> Vec<String> {
    let mut lines = Vec::new();
    for sensor in sensors {
        lines.push(sensor.describe());
    }
    lines
}
