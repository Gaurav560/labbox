//! Chapter 24: smart pointers. Box for a value that contains itself, Rc for shared owners, RefCell to change
//! something that is shared.
use std::cell::RefCell;
use std::rc::Rc;

/// Who to call about a fault, in order, until someone answers. Each step owns the rest of the chain.
#[derive(Debug, PartialEq)]
pub enum Escalation {
    Call(String),
    CallThen(String, Box<Escalation>),
}

impl Escalation {
    /// Everyone on the chain, first called first.
    pub fn people(&self) -> Vec<String> {
        match self {
            Escalation::Call(person) => vec![person.clone()],
            Escalation::CallThen(person, rest) => {
                let mut all = vec![person.clone()];
                all.extend(rest.people());
                all
            }
        }
    }
}

/// A chain from a list of contacts (the first is called first), or None for an empty list.
pub fn chain(contacts: &[&str]) -> Option<Escalation> {
    // TODO (task build_chain): match contacts. [] gives None; [last] gives Some(Escalation::Call(last.to_string()));
    //   [first, rest @ ..] gives Some(Escalation::CallThen(first.to_string(), Box::new(chain(rest)?))): the rest of
    //   the chain, built the same way, in a Box.
    let _ = contacts;
    todo!()
}

/// A repair crew and its list of jobs.
#[derive(Debug, Default)]
pub struct Crew {
    pub name: String,
    pub jobs: Vec<String>,
}

/// A turbine shares its crew with its neighbours: every turbine holds an Rc to the same RefCell<Crew>.
pub struct Turbine {
    pub id: String,
    pub crew: Rc<RefCell<Crew>>,
}

impl Turbine {
    /// Adds a job to the shared crew's list, like "T12: blade inspection".
    pub fn report_fault(&self, fault: &str) {
        // TODO (task shared_crew): the crew is shared, so it is behind Rc<RefCell<..>>. Borrow it mutably for this
        //   one line and push the job:  self.crew.borrow_mut().jobs.push(format!("{}: {}", self.id, fault));
        let _ = fault;
        todo!()
    }
}
