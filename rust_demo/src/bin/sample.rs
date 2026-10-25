//! A small weather report, written to show off Tokyo Clear Night.
use std::collections::HashMap;
use std::fmt::{self, Display};

const MAX_CITIES: usize = 8;

#[derive(Debug, Clone, PartialEq)]
enum Weather {
    Sunny,
    Rain { mm: f64 },
    Snow(u8),
}

trait Describe {
    fn describe(&self) -> String;
}

#[derive(Debug, Clone)]
struct City {
    name: String,
    weather: Weather,
    temps: Vec<i32>,
}

impl City {
    fn new(name: &str, weather: Weather) -> Self {
        Self { name: name.to_string(), weather, temps: vec![21, 19, 24] }
    }

    fn warmest(&self) -> Option<i32> {
        self.temps.iter().copied().max()
    }

    fn into_name(self) -> String {
        self.name
    }
}

impl Describe for City {
    fn describe(&self) -> String {
        match &self.weather {
            Weather::Sunny => format!("{} is sunny", self.name),
            Weather::Rain { mm } if *mm > 10.0 => format!("{} is soaked", self.name),
            Weather::Rain { .. } => format!("{} has light rain", self.name),
            Weather::Snow(cm) => format!("{} has {cm} cm of snow", self.name),
        }
    }
}

impl Display for City {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({})", self.name, self.describe())
    }
}

fn parse_temp(text: &str) -> Result<i32, std::num::ParseIntError> {
    let value: i32 = text.trim().parse()?;
    Ok(value)
}

fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let mut cities = vec![
        City::new("Tokyo", Weather::Sunny),
        City::new("Osaka", Weather::Rain { mm: 12.5 }),
        City::new("Sapporo", Weather::Snow(30)),
    ];
    cities.truncate(MAX_CITIES);

    let mut by_name: HashMap<String, usize> = HashMap::new();
    for (i, city) in cities.iter().enumerate() {
        by_name.insert(city.name.clone(), i);
        println!("{city}");
    }

    let warm: Vec<i32> = cities.iter().filter_map(|c| c.warmest()).collect();
    let names: Vec<String> = cities.into_iter().map(City::into_name).collect();
    let temp = parse_temp(" 23 ").unwrap();
    assert_eq!(longest("Tokyo", "Osaka"), "Tokyo");
    println!("{names:?} {warm:?} {temp} {}", temp as f64 / 2.0);
}
