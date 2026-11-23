// Chapter 24: run it with  cargo run
use std::cell::RefCell;
use std::rc::Rc;

use ch24_smart_pointers::{chain, Crew, Turbine};

fn main() {
    let calls = chain(&["shift engineer", "site manager", "turbine maker's hotline"]).unwrap();
    println!("{calls:?}");
    println!("call in order: {:?}", calls.people());

    let north = Rc::new(RefCell::new(Crew { name: "North crew".into(), jobs: vec![] }));
    let t12 = Turbine { id: "T12".into(), crew: Rc::clone(&north) };
    let t19 = Turbine { id: "T19".into(), crew: Rc::clone(&north) };
    println!("owners of the North crew: {}", Rc::strong_count(&north));

    t12.report_fault("blade inspection");
    t19.report_fault("yaw motor noise");
    println!("{}: {:?}", north.borrow().name, north.borrow().jobs);

    drop(t19);
    println!("owners after T19 is removed: {}", Rc::strong_count(&north));
}
