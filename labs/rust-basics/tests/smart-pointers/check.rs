use ch24_smart_pointers::*;
use std::cell::RefCell;
use std::rc::Rc;

#[test]
fn labbox_checks() {
    task("build_chain", || {
        let got = chain(&["engineer", "manager", "hotline"]);
        let want = Escalation::CallThen("engineer".into(), Box::new(Escalation::CallThen("manager".into(), Box::new(Escalation::Call("hotline".into())))));
        if got.as_ref() != Some(&want) {
            return Err(differs("Each step owns the rest of the chain in a Box.", Some(&want), got.as_ref()));
        }
        if chain(&[]).is_some() || chain(&["solo"]) != Some(Escalation::Call("solo".into())) {
            return Err(fail("An empty list gives None; one contact gives Call(that contact)."));
        }
        Ok("A chain that contains itself, one Box at a time.".into())
    });
    task("shared_crew", || {
        let crew = Rc::new(RefCell::new(Crew { name: "North".into(), jobs: vec![] }));
        let a = Turbine { id: "T12".into(), crew: Rc::clone(&crew) };
        let b = Turbine { id: "T19".into(), crew: Rc::clone(&crew) };
        a.report_fault("blade inspection");
        b.report_fault("yaw motor noise");
        let jobs = crew.borrow().jobs.clone();
        if jobs != vec!["T12: blade inspection".to_string(), "T19: yaw motor noise".to_string()] {
            return Err(differs("Both turbines' jobs should land in the one shared crew.", ["T12: blade inspection", "T19: yaw motor noise"], jobs));
        }
        Ok("Two owners, one crew: Rc shared it, RefCell let each owner change it in turn.".into())
    });
}
