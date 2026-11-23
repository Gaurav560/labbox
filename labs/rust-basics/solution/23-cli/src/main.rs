// Chapter 23: the windwatch program.  cargo run -- --help   or   cargo run -- data/farm.csv --turbine T07
use clap::Parser;

use ch23_cli::{run, Args};

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    for line in run(&args)? {
        println!("{line}");
    }
    Ok(())
}
