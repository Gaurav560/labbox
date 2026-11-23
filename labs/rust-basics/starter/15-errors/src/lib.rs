//! Chapter 15: errors you can handle, with Result and the ? operator.

#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

/// One field as a number, or an error message that says which field and what it contained.
pub fn number(field: &str, what: &str) -> Result<f64, String> {
    // TODO (task number): match field.trim().parse::<f64>(): Ok(value) gives Ok(value); Err(_) gives
    //   Err(format!("{what} is not a number: {field:?}")).
    todo!()
}

/// A log line "T07,time,wind,kW" as a Reading, or an error message that says exactly what is wrong.
pub fn parse_reading(line: &str) -> Result<Reading, String> {
    let parts: Vec<&str> = line.split(',').collect();
    if parts.len() != 4 {
        return Err(format!("expected 4 fields, found {}", parts.len()));
    }
    // TODO (task parse_reading): let wind_ms = number(parts[2], "wind speed")?;  and the same for power_kw
    //   ("power"). The ? returns the error to the caller at once. Then Ok(Reading { turbine: parts[0].to_string(),
    //   wind_ms, power_kw }).
    todo!()
}
