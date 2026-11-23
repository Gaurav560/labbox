use ch06_ownership::*;

#[test]
fn labbox_checks() {
    task("fix_moved_value", || {
        let (mut working, backup) = with_backup(vec![2100.0, 2250.0]);
        working.push(1.0);
        if backup != vec![2100.0, 2250.0] || working != vec![2100.0, 2250.0, 1.0] {
            return Err(differs("The backup must be a separate copy: let backup = log.clone();", "[2100.0, 2250.0]", format!("{backup:?}")));
        }
        Ok("It compiles: clone() made a second vector, so both names own their own data.".into())
    });
    task("add_reading", || {
        let got = add_reading(vec![2100.0], 2400.0);
        if got != vec![2100.0, 2400.0] {
            return Err(differs("Push the reading, then return the log as the last expression.", "[2100.0, 2400.0]", format!("{got:?}")));
        }
        let got = add_reading(Vec::new(), 5.0);
        if got != vec![5.0] {
            return Err(differs("An empty log gets its first reading.", "[5.0]", format!("{got:?}")));
        }
        Ok("The log moved in, changed, and moved back out: ownership passed both ways.".into())
    });
}
