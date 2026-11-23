// Chapter 12: run it with  cargo run
use ch12_modules::reading::parse_line;
use ch12_modules::summary_text;

fn main() {
    let lines = [
        "T07,2026-11-24 10:10,12.4,2100",
        "T07,2026-11-24 10:20,12.9,2180",
        "T12,2026-11-24 10:10,3.1,60",
        "T12,2026-11-24 10:20,windy,0",
        "T31,2026-11-24 10:10,25.6,0",
    ];
    println!("{}", summary_text(&lines));
    println!("first line: {:?}", parse_line(lines[0]));
}
