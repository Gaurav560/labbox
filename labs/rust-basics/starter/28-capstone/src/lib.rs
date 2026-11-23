//! Chapter 28: Windwatch as a web service. Turbines post readings; the control room asks for summaries.
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::routing::{get, post};
use axum::{Json, Router};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct Summary {
    pub turbine: String,
    pub readings: usize,
    pub average_kw: f64,
    pub underperforming: usize,
}

/// Every reading, by turbine, shared by all requests (Arc), changed one request at a time (Mutex).
pub type Store = Arc<Mutex<HashMap<String, Vec<Reading>>>>;

/// The power curve of chapter 9.
pub fn expected_kw(wind_ms: f64) -> f64 {
    if wind_ms < 3.0 || wind_ms >= 25.0 { 0.0 } else if wind_ms >= 12.0 { 2_500.0 } else { 2_500.0 * ((wind_ms - 3.0) / 9.0).powi(3) }
}

pub fn app(store: Store) -> Router {
    Router::new()
        .route("/health", get(|| async { "ok" }))
        .route("/readings", post(add_reading))
        .route("/turbines/{id}/summary", get(summary))
        .with_state(store)
}

/// POST /readings with a JSON Reading. 201 when stored, 422 when the power is impossible.
pub async fn add_reading(State(store): State<Store>, Json(reading): Json<Reading>) -> StatusCode {
    // TODO (task post_reading): refuse impossible power (below 0.0 or above 2_500.0) with
    //   StatusCode::UNPROCESSABLE_ENTITY. Otherwise lock the store and push the reading under its turbine:
    //   store.lock().unwrap().entry(reading.turbine.clone()).or_default().push(reading);  then StatusCode::CREATED.
    let _ = (store, reading);
    StatusCode::NOT_IMPLEMENTED
}

/// GET /turbines/{id}/summary. 404 for a turbine with no readings.
pub async fn summary(State(store): State<Store>, Path(id): Path<String>) -> Result<Json<Summary>, StatusCode> {
    // TODO (task summary_route): lock the store; store.get(&id).ok_or(StatusCode::NOT_FOUND)? gives the readings or a
    //   404. Then build the Summary: readings.len(), the average power, and how many readings are below 80% of
    //   expected_kw(r.wind_ms) (only where something is expected), and return Ok(Json(Summary { ... })).
    let _ = (store, id);
    Err(StatusCode::NOT_IMPLEMENTED)
}
