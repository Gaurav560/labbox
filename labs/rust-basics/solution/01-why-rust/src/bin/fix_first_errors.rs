// Chapter 1: three small mistakes, fixed with the compiler's help. Run it with:  cargo run --bin fix_first_errors
fn main() {
    let turbines = 40;
    let rated_mw = 2.5;
    println!("Turbines: {turbines}");
    println!("Capacity: {} MW", turbines as f64 * rated_mw);
}
