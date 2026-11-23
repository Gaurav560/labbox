//! Chapter 22: the code under test. The power curve and a log-line parser, as Windwatch uses them.

/// Expected power at a wind speed, in kW: nothing below 3 m/s or from 25 m/s, 2500 from 12 m/s, a cube in between.
pub fn power_curve(wind_ms: f64) -> f64 {
    if wind_ms < 3.0 || wind_ms >= 25.0 {
        0.0
    } else if wind_ms >= 12.0 {
        2_500.0
    } else {
        2_500.0 * ((wind_ms - 3.0) / 9.0).powi(3)
    }
}

/// "T07,time,wind,kW" as (turbine, wind, power), or an error message.
pub fn parse(line: &str) -> Result<(String, f64, f64), String> {
    let parts: Vec<&str> = line.split(',').collect();
    if parts.len() != 4 {
        return Err(format!("expected 4 fields, found {}", parts.len()));
    }
    let wind: f64 = parts[2].trim().parse().map_err(|_| format!("bad wind {:?}", parts[2]))?;
    let power: f64 = parts[3].trim().parse().map_err(|_| format!("bad power {:?}", parts[3]))?;
    Ok((parts[0].to_string(), wind, power))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn full_power_from_12_ms() {
        assert_eq!(power_curve(12.0), 2_500.0);
    }
}
