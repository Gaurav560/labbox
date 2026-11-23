// Chapter 6: run it with  cargo run
use ch06_ownership::{add_reading, with_backup};

fn main() {
    let log = vec![2100.0, 2250.0, 1980.0];
    let log = add_reading(log, 2400.0); // log moves in, and a log comes back out
    println!("T07 log: {log:?}");

    let (mut working, backup) = with_backup(log);
    working.clear(); // the working copy is emptied; the backup is a separate copy
    println!("working: {working:?}, backup: {backup:?}");

    let rated = 2500; // a u32 is Copy: assigning copies it, nothing moves
    let also_rated = rated;
    println!("rated {rated}, also {also_rated}");

    let site = String::from("Kutch Coast");
    let name = site; // a String moves: `site` is no longer usable
    println!("site: {name}");
}
