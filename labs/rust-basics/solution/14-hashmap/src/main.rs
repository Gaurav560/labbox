// Chapter 14: run it with  cargo run
use std::collections::BTreeMap;

use ch14_hashmap::{energy_by_turbine, silent_turbines};

fn main() {
    let lines = [
        "T07,10:10,12.4,2100", "T12,10:10,7.5,140", "T31,10:10,13.0,2500",
        "T07,10:20,12.9,2180", "T12,10:20,7.9,165", "T31,10:20,windy,0",
        "T07,10:30,13.3,2240", "T19,10:30,7.5,305",
    ];
    let energy = energy_by_turbine(&lines);
    println!("HashMap, in its own order:");
    for (turbine, kwh) in &energy {
        println!("  {turbine}: {kwh:.1} kWh");
    }

    let sorted: BTreeMap<_, _> = energy.iter().collect();
    println!("BTreeMap, sorted by key: {sorted:?}");
    println!("T07 made {:.1} kWh; T40 made {:?}", energy["T07"], energy.get("T40"));

    let farm: Vec<String> = (1..=40).map(|n| format!("T{n:02}")).collect();
    let farm: Vec<&str> = farm.iter().map(|s| s.as_str()).collect();
    let reported: Vec<&str> = lines.iter().map(|l| &l[..3]).collect();
    let silent = silent_turbines(&farm, &reported);
    println!("{} of 40 turbines are silent; the first five: {:?}", silent.len(), &silent[..5]);
}
