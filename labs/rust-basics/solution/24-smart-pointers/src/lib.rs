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
    match contacts {
        [] => None,
        [last] => Some(Escalation::Call(last.to_string())),
        [first, rest @ ..] => Some(Escalation::CallThen(first.to_string(), Box::new(chain(rest)?))),
    }
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
        self.crew.borrow_mut().jobs.push(format!("{}: {}", self.id, fault));
    }
}
