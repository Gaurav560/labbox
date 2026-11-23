//! Chapter 17: generics. One function or type, for many types, checked by the compiler.

/// The largest item of any list whose items can be compared and copied: power readings, fault codes, hours.
pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> Option<T> {
    // TODO (task largest): start with  let mut best = *items.first()?;  (the ? returns None for an empty list),
    //   keep the largest in  for &item in items { ... }, and return Some(best). Works for any T the bounds allow.
    todo!()
}

/// A named series of values of any one type: kW readings (f64), fault codes (u16), ...
#[derive(Debug, Clone)]
pub struct Series<T> {
    pub name: String,
    pub values: Vec<T>,
}

impl<T: PartialOrd + Copy> Series<T> {
    pub fn new(name: &str) -> Series<T> {
        Series { name: name.to_string(), values: Vec::new() }
    }

    pub fn push(&mut self, value: T) {
        self.values.push(value);
    }

    /// The series' largest value, if it has any.
    pub fn peak(&self) -> Option<T> {
        // TODO (task series_peak): the generic function above already does this for any T: call it on
        //   &self.values and return its answer.
        todo!()
    }
}
