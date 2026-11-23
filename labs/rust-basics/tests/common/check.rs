// Hidden checks: one @@RESULT line per task. A panic, or a todo!() still in your code, becomes a kind "not yet".
#![allow(dead_code)]
use std::fmt::Debug;
use std::panic::{self, AssertUnwindSafe};

fn esc(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', "\\n")
}

fn report(task: &str, passed: bool, message: &str, expected: Option<String>, actual: Option<String>) {
    let mut line = format!("{{\"task\": \"{}\", \"passed\": {}, \"message\": \"{}\"", esc(task), passed, esc(message));
    if let (Some(e), Some(a)) = (expected, actual) {
        line += &format!(", \"expected\": \"{}\", \"actual\": \"{}\"", esc(&e), esc(&a));
    }
    println!("@@RESULT {line}}}");
}

pub struct Fail {
    msg: String,
    expected: Option<String>,
    actual: Option<String>,
}

/// A failure with a message only.
pub fn fail(msg: &str) -> Fail {
    Fail { msg: msg.to_string(), expected: None, actual: None }
}

/// A failure that also shows what was expected and what your code gave.
pub fn differs(msg: &str, expected: impl Debug, actual: impl Debug) -> Fail {
    Fail { msg: msg.to_string(), expected: Some(format!("{expected:?}")), actual: Some(format!("{actual:?}")) }
}

/// Two floats equal to 0.001.
pub fn close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-3
}

/// Runs one task's check; your code's panics are caught and explained.
pub fn task(name: &str, check: impl FnOnce() -> Result<String, Fail>) {
    panic::set_hook(Box::new(|_| {}));
    let outcome = panic::catch_unwind(AssertUnwindSafe(check));
    let _ = panic::take_hook();
    match outcome {
        Ok(Ok(msg)) => report(name, true, &msg, None, None),
        Ok(Err(f)) => report(name, false, &format!("Not yet: {}", f.msg), f.expected, f.actual),
        Err(payload) => {
            let text = payload
                .downcast_ref::<&str>()
                .map(|s| s.to_string())
                .or_else(|| payload.downcast_ref::<String>().cloned())
                .unwrap_or_default();
            let msg = if text.contains("not yet implemented") {
                "Not yet: this function still says todo!(). Replace the todo!() with your code.".to_string()
            } else {
                format!("Not yet: your code panicked: {text}")
            };
            report(name, false, &msg, None, None);
        }
    }
}
