use axum::body::Body;
use axum::http::{Request, StatusCode};
use axum::Router;
use ch28_capstone::*;
use http_body_util::BodyExt;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tower::ServiceExt;

async fn post(app: &Router, json: &str) -> StatusCode {
    let req = Request::post("/readings").header("content-type", "application/json").body(Body::from(json.to_string())).unwrap();
    app.clone().oneshot(req).await.unwrap().status()
}

async fn get(app: &Router, path: &str) -> (StatusCode, String) {
    let resp = app.clone().oneshot(Request::get(path).body(Body::empty()).unwrap()).await.unwrap();
    let status = resp.status();
    let bytes = resp.into_body().collect().await.unwrap().to_bytes();
    (status, String::from_utf8(bytes.to_vec()).unwrap())
}

#[test]
fn labbox_checks() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    task("post_reading", || {
        let store: Store = Arc::new(Mutex::new(HashMap::new()));
        let app = app(store.clone());
        let ok = rt.block_on(post(&app, r#"{"turbine":"T12","wind_ms":7.5,"power_kw":140}"#));
        let glitch = rt.block_on(post(&app, r#"{"turbine":"T12","wind_ms":8.1,"power_kw":9999}"#));
        if ok != StatusCode::CREATED || glitch != StatusCode::UNPROCESSABLE_ENTITY {
            return Err(differs("201 for a good reading, 422 for power above 2,500 kW.", "201, 422", format!("{}, {}", ok.as_u16(), glitch.as_u16())));
        }
        let kept = store.lock().unwrap().get("T12").map(|v| v.len()).unwrap_or(0);
        if kept != 1 {
            return Err(differs("Only the good reading is stored, under T12.", 1, kept));
        }
        Ok("POST /readings stored the good reading and refused the glitch.".into())
    });
    task("summary_route", || {
        let store: Store = Arc::new(Mutex::new(HashMap::new()));
        store.lock().unwrap().insert("T12".into(), vec![
            Reading { turbine: "T12".into(), wind_ms: 7.5, power_kw: 140.0 },
            Reading { turbine: "T12".into(), wind_ms: 7.5, power_kw: 300.0 },
        ]);
        let app = app(store);
        let (status, body) = rt.block_on(get(&app, "/turbines/T12/summary"));
        if status != StatusCode::OK {
            return Err(differs("GET /turbines/T12/summary should answer 200.", 200, status.as_u16()));
        }
        let s: Summary = serde_json::from_str(&body).map_err(|e| format!("the answer is not a Summary: {e}: {body}"))?;
        if s.readings != 2 || !close(s.average_kw, 220.0) || s.underperforming != 1 {
            return Err(differs("2 readings, average 220 kW, 1 below 80% of the curve's 312.5.", "readings 2, average_kw 220, underperforming 1", &body));
        }
        let (missing, _) = rt.block_on(get(&app, "/turbines/T99/summary"));
        if missing != StatusCode::NOT_FOUND {
            return Err(differs("A turbine with no readings is 404.", 404, missing.as_u16()));
        }
        Ok("The control room's question, answered as JSON over HTTP.".into())
    });
}
