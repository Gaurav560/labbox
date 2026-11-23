//! Your tests for Windwatch. Run them with:  cargo test
use ch22_testing::{parse, power_curve};

#[test]
fn power_curve_edges() {
    assert_eq!(power_curve(2.99), 0.0); // too calm
    assert_eq!(power_curve(3.0), 0.0); // the cube starts at zero
    assert!((power_curve(7.5) - 312.5).abs() < 0.01); // halfway up the cube
    assert_eq!(power_curve(24.9), 2_500.0); // still full power
    assert_eq!(power_curve(25.0), 0.0); // storm stop
}

#[test]
fn parse_rejects_broken_lines() {
    assert_eq!(parse("T07,10:10,12.4,2100"), Ok(("T07".to_string(), 12.4, 2100.0)));
    assert!(parse("T07,10:20,12.9").is_err());
    assert_eq!(parse("T07,10:50,13.4,22O0"), Err("bad power \"22O0\"".to_string()));
}
