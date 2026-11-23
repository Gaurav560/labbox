// Chapter 28: run it with  cargo run   (then, in another terminal, the curl commands from the lesson)
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use ch28_capstone::app;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let store = Arc::new(Mutex::new(HashMap::new()));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    println!("Windwatch listening on http://localhost:3000");
    axum::serve(listener, app(store)).await?;
    Ok(())
}
