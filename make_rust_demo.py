"""Generate rust_demo.ipynb and rust_demo/src/main.rs: every Rust element with its Tokyo Clear Night color.

Unlike make_python_demo.py the colors are not typed in: tokenize_rust.js runs rust-analyzer and VS Code's TextMate
grammar over rust_demo/src/main.rs and resolves each token against Tokyo Night, Tokyo Clear Night.
Needs VS Code with the rust-analyzer extension, node and npx (to unpack vscode-textmate from VS Code's asar once).
Open rust_demo/src/main.rs to see it live; notebook cells get TextMate colors only (rust-analyzer skips them).
"""
import copy
import glob
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
CRATE = ROOT / "rust_demo"
THEMES = ROOT / "themes/tokyo-clear-night-color-theme.json"
TOKYO_NIGHT = glob.glob(os.path.expanduser("~/.vscode/extensions/enkia.tokyo-night-*/themes/tokyo-night-color-theme.json"))[0]
RA_EXT = glob.glob(os.path.expanduser("~/.vscode/extensions/rust-lang.rust-analyzer-*"))[0]
NM = Path(tempfile.gettempdir()) / "vscode-node-modules"

# Unused colors: greedy max-min distance (CIELAB) from every foreground in the theme; first two are from the starship prompt.
PALETTE = [
    ("Amber", "#ffc107", "starship auto-mode line"), ("Blush", "#f5c2e7", "starship git branch"),
    ("Green", "#55e755", "furthest from everything"), ("Spring", "#55e7a3", ""), ("Indigo", "#5555e7", ""),
    ("Lime", "#d3e755", ""), ("Magenta", "#e755dd", ""), ("Cream", "#eaf094", ""), ("Orchid", "#f094e3", ""),
    ("Azure", "#5572e7", ""), ("Mint", "#79ec81", ""), ("Raspberry", "#e75599", ""),
]

# (legend title, [snippets searched in this section's code; "text#2" = second occurrence], code)
SECTIONS = [
    ("Crate header", ["//! Crate-level doc comment.", "#!", "allow", "dead_code"], '''//! Crate-level doc comment.
#![allow(dead_code, unused_variables)]'''),

    ("Imports & modules", ["use", "as", "std", "collections", "HashMap", "fmt", "Display", "Ordering", "mod", "geometry",
                           "pub", "ORIGIN", "distance", "::"], '''use std::collections::HashMap;
use std::fmt::{self, Display};
use std::sync::atomic::{AtomicUsize, Ordering};

mod geometry {
    pub const ORIGIN: (i32, i32) = (0, 0);
    pub fn distance(a: (i32, i32), b: (i32, i32)) -> f64 {
        (((a.0 - b.0).pow(2) + (a.1 - b.1).pow(2)) as f64).sqrt()
    }
}'''),

    ("Constants, statics, numbers & operators", ["MAX_SIZE", "COUNTER", "LEGACY", "static", "mut", "const", "let", "ratio", "total",
                                                  "3.14_f64", "0xFF", "0o755", "0b1010", "1_000_000u64", "u64", "true", "&&", "||",
                                                  "!", "==", ">=", "<<", "|#2", "^", "+=", "..=", "usize"], '''const MAX_SIZE: usize = 1_000;
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
}'''),

    ("Strings, chars & escapes", ['"Tokyo"', 'r"', 'r#"', 'b"', "'A'", "b'z'", "\\n", "\\x41", "\\u{1F5FC}", "{name:>10}", "{}", "{greeting}",
                                  "format", "println", "!"], '''fn strings_and_chars() {
    let name = "Tokyo";
    let greeting = format!("Hello {name:>10}, {} letters\\n", name.len());
    let raw = r"C:\\Users\\night";
    let raw_hashes = r#"say "hi""#;
    let bytes = b"\\x41\\x42";
    let letter = 'A';
    let byte = b'z';
    let unicode = '\\u{1F5FC}';
    let multi = "line one \\
                 line two";
    println!("{greeting} {raw} {raw_hashes} {bytes:?} {letter} {byte} {unicode} {multi}");
}'''),

    ("Comments & doc comments", ["// A regular comment", "TODO", "FIXME", "XXX", "/* A block comment */", "/// Doc comment", "[`intra_doc_link`]",
                                 "```", "let#1", "x", "1"], '''// A regular comment
// TODO: tag inside a comment; FIXME and XXX too
/* A block comment */
/// Doc comment on a function, with `code` and [`intra_doc_link`].
///
/// ```
/// let x = 1;
/// ```
fn documented() {}

fn intra_doc_link() {}'''),

    ("Structs, impl & traits", ["derive", "Debug", "Wrapper", "T", "Describe", "KIND", "Output", "describe", "String", "City", "population",
                                "name", "tags", "CAPITAL", "Self", "&self", "&mut self", "self", "new", "tokyo", "label", "rename",
                                "into_name", "to_string", "Vec", "fmt", "Display", "write", "impl", "trait", "struct", "fn", "for"],
     '''/// Generic wrapper.
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
}'''),

    ("Generics, lifetimes & type aliases", ["Pair", "K", "'a", "first", "largest", "zeroed", "N", "Option", "Clone", "PartialOrd", "where", "u8"], '''type Pair<K, V> = (K, V);

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
}'''),

    ("Enums, unions & match", ["Weather", "Clear", "Rain", "Snow", "mm", "IntOrFloat", "match", "if", "=>", "@", "..", "enum", "union"], '''#[derive(Debug, Clone, Copy, PartialEq)]
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
}'''),

    ("Macros, attributes & tests", ["macro_rules", "square", "$", "expr", "#[deprecated", "note", "old_api", "cfg", "test", "super", "assert_eq", "9"], '''macro_rules! square {
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
}'''),

    ("Control flow, errors & unsafe", ["?", "Ok", "Some", "async", "unsafe", "danger", "'outer", "while", "let#8", "loop", "break", "continue",
                                       "|n|", "map", "collect", "iter", "fetch_add", "SeqCst", "squares", "city", "counts", "shadow"], '''fn parse(text: &str) -> Result<i32, std::num::ParseIntError> {
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
}'''),
]

# (element, snippet in the full file: "text#n" = nth occurrence). Colors and sources are looked up, never typed.
COMPARE = [
    ("Keyword: fn / use / impl", "fn#1"), ("Keyword: let / mod / const", "let#1"), ("Control-flow keyword", "match"),
    ("pub / static / mut", "pub#2"), ("Operator: logical / comparison", "&&"), ("Operator: other", "<<"),
    ("Function declaration", "numbers_and_operators"), ("Function call", "control_flow();"), ("Method call (own)", "rename#2"),
    ("Method call (std)", "to_string#1"), ("Associated function (std)", "new#1"), ("Macro call (std)", "println#1"),
    ("Macro `!`", "@println!"), ("Macro declaration", "square#1"),
    ("Parameter declaration", "population#2"), ("Parameter use", "name.to_string"), ("Variable declaration", "ratio#1"),
    ("Variable use", "ratio#2"), ("Mutable variable", "total#2"), ("Field declaration", "tags#1"), ("Field use", ".name = new"),
    ("`self` in signature", "self#4"), ("`self` in body", "self.name = new"), ("`Self`", "Self#1"),
    ("const", "MAX_SIZE"), ("static", "COUNTER#1"), ("Associated const", "CAPITAL"),
    ("Struct (own)", "Wrapper"), ("Struct (std)", "HashMap#2"), ("Enum (own)", "Weather#1"), ("Enum variant (declaration)", "Clear#1"),
    ("Enum variant (use)", "Clear#2"), ("`Some` / `Ok` / `None`", "Some#1"), ("Trait (own)", "Describe#1"), ("Trait (std)", "Display#2"),
    ("Type alias", "Pair"), ("Type parameter", "<T>"), ("Const generic", "N: usize"), ("Primitive type", "u8#1"), ("Module", "geometry#2"),
    ("Crate `std`", "std#1"), ("Lifetime", "'a#1"), ("Loop label", "'outer#1"),
    ("Attribute", "derive#1"), ("Derive argument", "Debug#1"), ("Deprecated", "old_api#2"),
    ("Number", "0xFF"), ("Number with suffix", "3.14_f64"), ("Bool", "true#1"), ("String", '"Tokyo"'), ("Format placeholder", "{name:>10}"),
    ("Byte char", "b'z'"), ("Escape", "\\n"), ("Comment", "// A regular comment"), ("Doc comment", "/// Doc comment"),
    ("Code in doc comment", "/// let x = 1;"), ("Intra-doc link", "[`intra_doc_link`]"), ("TODO tag", "TODO"),
]

ITALIC, BOLD = ";font-style:italic", ";font-weight:bold"
DECO = {"underline": "underline", "strikethrough": "line-through"}


def split_nth(snippet):
    m = re.fullmatch(r"(.+)#(\d+)", snippet)
    return (m[1], int(m[2])) if m else (snippet, 1)


def css(style):
    flags = set(style.split("+")) - {""}
    deco = " ".join(DECO[f] for f in DECO if f in flags)
    return (ITALIC if "italic" in flags else "") + (BOLD if "bold" in flags else "") + (f";text-decoration:{deco}" if deco else "")


def span(text, look):
    color, style = look
    return f'<span style="color:{color};font-family:monospace{css(style)}">{html.escape(text).replace("|", "&#124;")}</span>'


def tag(look):
    return span(look[0] + (" " + look[1].replace("+", " ") if look[1] else ""), look)


def tokenize(themes):
    if not NM.exists():
        subprocess.run(["npx", "--yes", "@electron/asar", "extract", "/usr/share/code/resources/app/node_modules.asar", str(NM)], check=True)
    env = os.environ | {"VSC_NM": str(NM), "RA_EXT": RA_EXT}
    r = subprocess.run(["node", str(ROOT / "tokenize_rust.js"), str(CRATE), *themes], env=env, check=True, capture_output=True, text=True)
    return json.loads(r.stdout)


class Lookup:
    def __init__(self, data, names):
        self.text, self.names = data["text"], names
        self.chars = {n: data["themes"][Path(n).name] for n in names}
        self.scopes = data["scopes"] + [None] * len(self.text)
        self.sem = {}
        for t in data["tokens"]:
            for i in range(t["len"]):
                self.sem[t["start"] + i] = t

    def find(self, snippet, lo=0, hi=None):
        at = snippet.startswith("@")  # "@println!" = color of its last char
        text, nth = split_nth(snippet.removeprefix("@"))
        pos = lo - 1
        for _ in range(nth):
            pos = self.text.find(text, pos + 1, hi)
            assert pos >= 0, f"snippet not found: {snippet}"
        return pos + (len(text) - 1 if at else next((i for i, ch in enumerate(text) if ch.isalnum()), 0))

    def look(self, pos, name):
        color, style = self.chars[name][pos]
        return color, style

    def source(self, pos):
        t, sc = self.sem.get(pos), self.scopes[pos]
        sem = f"{t['type']}" + "".join("." + m for m in t["mods"][:3]) if t else "no semantic token"
        return f"{sem} · {sc[-1].removesuffix('.rust') if sc else '-'}"


def legend(lk, name, title, snippets, code, start):
    rows = {}
    for s in snippets:
        pos = lk.find(s, start, start + len(code))
        rows.setdefault((lk.look(pos, name), lk.source(pos)), []).append(s)
    lines = [f"| {span('  '.join(split_nth(x.removeprefix('@'))[0] for x in snips), look)} | {tag(look)} | <code>{src}</code> |" for (look, src), snips in rows.items()]
    return f"## {title}\n\n| Element | Color | Semantic token · TextMate scope |\n|---|---|---|\n" + "\n".join(lines)


def comparison(lk, tn, tcn):
    rows = []
    for i, (label, snip) in enumerate(COMPARE, 1):
        pos = lk.find(snip)
        a, b = (lk.look(pos, n) for n in (tn, tcn))
        mark = "" if a == b else "changed"
        rows.append(f"| {i} | {label} | {span('Aa', a)} {tag(a)} | {span('Aa', b)} {tag(b)} | {mark} | <code>{lk.source(pos)}</code> |")
    changed = sum(1 for r in rows if "| changed |" in r)
    return (
        "# Tokyo Night vs Tokyo Clear Night\n\n"
        "Colors are resolved by running rust-analyzer and VS Code's TextMate grammar on `rust_demo/src/main.rs`, "
        "then applying each theme's rules. Tokyo Night has semantic highlighting off, so it only sees the grammar; "
        "Tokyo Clear Night turns it on, so rust-analyzer's tokens win. "
        f"**{changed} of {len(rows)} rows differ.**\n\n"
        "| # | Element | Tokyo Night | Tokyo Clear Night | | Semantic token · TextMate scope |\n|---|---|---|---|---|---|\n" + "\n".join(rows)
    )


def palette_md():
    rows = "\n".join(f"| {span(n, (c, ""))} | <code>{c}</code> | {note} |" for n, c, note in PALETTE)
    return ("# 12 unused colors\n\nFree colors for new rules, each at least 19 CIELAB units from every foreground the theme uses. "
            "The first two are from your starship prompt (amber is the auto-mode line, pink the git branch); the other starship colors "
            "(blue, teal, yellow) are within 14 of colors already used.\n\n"
            f"| Color | Hex | Note |\n|---|---|---|\n{rows}")


def cell(kind, src, i):
    base = {"cell_type": kind, "id": f"cell-{i}", "metadata": {}, "source": src}
    return base | ({"execution_count": None, "outputs": [], "metadata": {"vscode": {"languageId": "rust"}}} if kind == "code" else {})


def main():
    code = "\n\n".join(c for _, _, c in SECTIONS) + "\n"
    (CRATE / "src").mkdir(parents=True, exist_ok=True)
    (CRATE / "Cargo.toml").write_text('[package]\nname = "demo"\nversion = "0.1.0"\nedition = "2021"\n')
    (CRATE / "src/main.rs").write_text(code)
    theme = json.loads(THEMES.read_text())
    names = [TOKYO_NIGHT, str(THEMES)]
    lk = Lookup(tokenize(names), names)

    cells = [("markdown",
              "# Tokyo Clear Night: Rust colors\n\n"
              "Every Rust element and the color the theme gives it, resolved with rust-analyzer's semantic tokens "
              "(<code>semanticHighlighting</code> is on in this theme). Open `rust_demo/src/main.rs` for the live version: "
              "notebook cells below get TextMate colors only, because rust-analyzer does not analyze notebook cells. "
              "The colors in the tables are what the theme gives the same code in a `.rs` file.\n\n"
              "Check any token with **Developer: Inspect Editor Tokens and Scopes**.")]
    for title, snippets, section in SECTIONS:
        cells += [("markdown", legend(lk, names[1], title, snippets, section, code.index(section))), ("code", section)]
    cells += [("markdown", comparison(lk, *names)), ("markdown", palette_md())]
    nb = {"cells": [cell(k, s, i) for i, (k, s) in enumerate(cells)],
          "metadata": {"language_info": {"name": "rust"}}, "nbformat": 4, "nbformat_minor": 5}
    out = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "rust_demo.ipynb")
    Path(out).write_text(json.dumps(nb, indent=1) + "\n")
    print(f"{out}: {len(cells)} cells")


if __name__ == "__main__":
    main()
