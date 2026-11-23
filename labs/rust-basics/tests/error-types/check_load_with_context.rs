use ch16_error_types::*;

#[test]
fn labbox_checks() {
    task("load_with_context", || {
        let dir = std::env::temp_dir();
        let good = dir.join("labbox_good.log");
        let bad = dir.join("labbox_bad.log");
        std::fs::write(&good, "T07,a,12.4,2100\nT07,b,12.9,2180\n").unwrap();
        std::fs::write(&bad, "T12,a,7.5,140\nT12,b,7.9\n").unwrap();
        let got = load(good.to_str().unwrap()).map_err(|e| format!("{e:#}"))?;
        if got.len() != 2 {
            return Err(differs("A good file gives every reading.", 2, got.len()));
        }
        let err = load(bad.to_str().unwrap()).expect_err("a broken line must be an error");
        let text = format!("{err:#}");
        if !text.contains("line 2") || !text.contains("expected 4 fields, found 3") {
            return Err(differs("The error should say the file and line, then the cause: with_context(|| format!(\"{path}, line {}\", n + 1)).", "...labbox_bad.log, line 2: expected 4 fields, found 3", text));
        }
        let err = load("/nowhere/t99.log").expect_err("a missing file must be an error");
        let text = format!("{err:#}");
        if !text.contains("cannot read /nowhere/t99.log") {
            return Err(differs("A missing file should say: cannot read <path>.", "cannot read /nowhere/t99.log: No such file ...", text));
        }
        Ok("Errors that say where (file, line) and why (the cause underneath).".into())
    });
}
