// Chapter 1: three small mistakes, fixed with the compiler's help. Run it with:  cargo run --bin fix_first_errors
// TODO (task fix_first_errors): this program has three mistakes. Run it, read what the compiler says, fix one, and
//   run it again, until it prints:
//   Turbines: 40
//   Capacity: 100 MW
fn main() {
    let turbines = 40;
    let rated_mw = 2.5
    println("Turbines: {turbines}");
    println!("Capacity: {} MW", turbines * rated_mw);
}
