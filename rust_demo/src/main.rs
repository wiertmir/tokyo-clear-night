//! Crate-level doc comment.
#![allow(dead_code, unused_variables)]

use std::collections::HashMap;
use std::fmt::{self, Display};
use std::sync::atomic::{AtomicUsize, Ordering};

mod geometry {
    pub const ORIGIN: (i32, i32) = (0, 0);
    pub fn distance(a: (i32, i32), b: (i32, i32)) -> f64 {
        (((a.0 - b.0).pow(2) + (a.1 - b.1).pow(2)) as f64).sqrt()
    }
}

const MAX_SIZE: usize = 1_000;
static COUNTER: AtomicUsize = AtomicUsize::new(0);
static mut LEGACY: u32 = 0;

fn numbers_and_operators() {
    let ratio = 3.14_f64 * 2.0 / 7.0;
    let (mask, octal, binary, big) = (0xFF, 0o755, 0b1010, 1_000_000u64);
    let ok = ratio > 1.0 && !(mask == 0) || big >= 3;
    let shifted = (mask << 2) | (octal & binary) ^ 1;
    let mut total = 0;
    total += shifted;
    let range = 0..=9;
    let flags = [true, false];
}

fn strings_and_chars() {
    let name = "Tokyo";
    let greeting = format!("Hello {name:>10}, {} letters\n", name.len());
    let raw = r"C:\Users\night";
    let raw_hashes = r#"say "hi""#;
    let bytes = b"\x41\x42";
    let letter = 'A';
    let byte = b'z';
    let unicode = '\u{1F5FC}';
    let multi = "line one \
                 line two";
    println!("{greeting} {raw} {raw_hashes} {bytes:?} {letter} {byte} {unicode} {multi}");
}

// A regular comment
// TODO: tag inside a comment; FIXME and XXX too
/* A block comment */
/// Doc comment on a function, with `code` and [`intra_doc_link`].
///
/// ```
/// let x = 1;
/// ```
fn documented() {}

fn intra_doc_link() {}

/// Generic wrapper.
#[derive(Debug, Clone, PartialEq)]
struct Wrapper<T> {
    value: T,
}

trait Describe {
    const KIND: &'static str;
    type Output;
    fn describe(&self) -> Self::Output;
    fn name(&self) -> String {
        String::from("unnamed")
    }
}

#[derive(Debug, Default)]
pub struct City {
    pub name: String,
    population: u64,
    tags: Vec<String>,
}

impl City {
    pub const CAPITAL: bool = true;

    pub fn new(name: &str, population: u64) -> Self {
        Self { name: name.to_string(), population, tags: Vec::new() }
    }

    pub fn tokyo() -> City {
        City::new("Tokyo", 14_000_000)
    }

    pub fn label(&self) -> String {
        format!("{} ({})", self.name, self.population)
    }

    pub fn rename(&mut self, new_name: &str) {
        self.name = new_name.to_string();
    }

    pub fn into_name(self) -> String {
        self.name
    }
}

impl Describe for City {
    const KIND: &'static str = "city";
    type Output = String;
    fn describe(&self) -> Self::Output {
        self.label()
    }
}

impl Display for City {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.label())
    }
}

type Pair<K, V> = (K, V);

fn first<'a, T: Clone + 'a>(items: &'a [T]) -> Option<&'a T> {
    items.first()
}

fn largest<T>(items: &[T]) -> &T
where
    T: PartialOrd,
{
    let mut best = &items[0];
    for item in items {
        if item > best {
            best = item;
        }
    }
    best
}

fn zeroed<const N: usize>() -> [u8; N] {
    [0; N]
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Weather {
    Clear,
    Rain { mm: f32 },
    Snow(u8),
}

union IntOrFloat {
    i: u32,
    f: f32,
}

fn weather_report(w: Weather) -> &'static str {
    match w {
        Weather::Clear => "clear",
        Weather::Rain { mm } if mm > 10.0 => "downpour",
        Weather::Rain { .. } => "rain",
        Weather::Snow(depth @ 1..=5) => "light snow",
        Weather::Snow(_) => "snow",
    }
}

macro_rules! square {
    ($x:expr) => {
        $x * $x
    };
}

#[deprecated(note = "use weather_report")]
fn old_api() {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        assert_eq!(square!(3), 9);
    }
}

fn parse(text: &str) -> Result<i32, std::num::ParseIntError> {
    let n: i32 = text.trim().parse()?;
    Ok(n)
}

async fn fetch() -> String {
    String::from("done")
}

unsafe fn danger(p: *const u32) -> u32 {
    *p
}

fn control_flow() {
    let mut city = City::tokyo();
    city.rename("Osaka");
    let weather = Weather::Rain { mm: 12.5 };
    let items = vec![3, 1, 2];
    let squares: Vec<i32> = items.iter().map(|n| n * n).collect();
    let mut counts: HashMap<String, usize> = HashMap::new();
    'outer: for i in 0..3 {
        while let Some(x) = squares.get(i) {
            if *x > 4 {
                break 'outer;
            }
            continue 'outer;
        }
    }
    let label = loop {
        break city.describe();
    };
    let shadow = if let Some(first_item) = first(&items) { *first_item } else { 0 };
    let value = unsafe { danger(&1u32) };
    COUNTER.fetch_add(1, Ordering::SeqCst);
    old_api();
    println!("{label} {value} {shadow} {}", weather_report(weather));
}

fn main() {
    control_flow();
    let _ = parse("42");
    let _ = geometry::distance(geometry::ORIGIN, (3, 4));
}
