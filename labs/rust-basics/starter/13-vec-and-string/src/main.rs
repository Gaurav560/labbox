// Chapter 13: run it with  cargo run
use ch13_vec_and_string::{as_sentence, moving_average};

fn main() {
    // T07, one reading every ten minutes: a gust at 10:30, then a drop
    let log = vec![2100.0, 2180.0, 2490.0, 1650.0, 2210.0, 2240.0];
    println!("readings: {log:?}");
    println!("average of 3: {:?}", moving_average(&log, 3));

    let mut sorted = log.clone();
    sorted.sort_by(|a, b| a.total_cmp(b)); // f64 has no plain sort(): see the chapter
    println!("lowest {}, highest {}", sorted[0], sorted[sorted.len() - 1]);

    let mut ids = vec!["T31", "T07", "T12", "T07"];
    ids.sort();
    ids.dedup();
    println!("underperforming: {}", as_sentence(&ids));
    println!("faulty: {}", as_sentence(&[]));

    let mut alert = String::from("Windwatch: ");
    alert.push_str(&as_sentence(&ids[..1]));
    alert += " needs a visit";
    println!("{alert} ({} bytes, room for {})", alert.len(), alert.capacity());
}
