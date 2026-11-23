//! Your tests for Windwatch. Run them with:  cargo test
use ch22_testing::{parse, power_curve};

#[test]
fn power_curve_edges() {
    // TODO (task test_curve): assert the power curve at its edges: 2.99 and 3.0 give 0.0, 7.5 gives about 312.5
    //   (compare with .abs() < 0.01), 24.9 gives 2_500.0, and 25.0 gives 0.0. Use assert_eq! and assert!.
}

#[test]
fn parse_rejects_broken_lines() {
    // TODO (task test_parse): assert that a good line parses to Ok(("T07".to_string(), 12.4, 2100.0)), that a line
    //   with three fields is_err(), and that "T07,10:50,13.4,22O0" gives Err("bad power \"22O0\"".to_string()).
}
