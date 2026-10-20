"""Generate python_demo.ipynb: every Python element with its Tokyo Clear Night color, plus a proposal.

Each legend row lists the exact snippets it describes; the build fails if a snippet is missing from its code cell.
"""
import ast
import html
import json
import sys

ITALIC, BOLD, STRIKE = ";font-style:italic", ";font-weight:bold", ";text-decoration:line-through"


def c(color, text, style=""):
    return f'<span style="color:{color};font-family:monospace{style}">{html.escape(text).replace("|", "&#124;")}</span>'


# (snippets that must appear in the code, color, style, source/notes)
SECTIONS = [
    ("Imports & modules", [
        (["import", "from", "as"], "#7dcfff", "", "keyword.control.import (Tokyo Night)"),
        (["os", "re", "collections", "dataclasses"], "#98a288", "", "semantic module (Cool Steel toward olive)"),
        (["Counter", "Enum"], "#45b1e8", "", "semantic class (Fresh Sky)"),
        (["dataclass", "field"], "#7aa2f7", "", "semantic function"),
    ], '''import os
import re as regex
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from warnings import deprecated'''),

    ("Constants, numbers & operators", [
        (["MAX_SIZE"], "#e1a58c", "", "semantic variable.readonly; plain #c0caf5 if Pylance doesn't mark it read-only"),
        (["1_000", "3.14", "0xFF", "0o755", "0b1010", "2j"], "#f19cbb", "", "constant.numeric (Pink Mist)"),
        (["None", "True", "False"], "#ff9e64", "", "constant.language"),
        (["..."], "#e0af68", "", "constant.other.ellipsis"),
        (["ratio", "mask", "flags"], "#c0caf5", "", "semantic variable.declaration"),
        (["=", "*", "**", "//", "%", ">"], "#89ddff", "", "keyword.operator"),
        (["and", "not", "or", "is", "in"], "#bb9af7", "", "keyword.operator.logical"),
        (["(", ")", "[", "]", ","], "#89ddff", "", "punctuation"),
    ], '''MAX_SIZE = 1_000
ratio = 3.14 * 2 ** 3 // 1 % 7
mask, octal, binary, imaginary = 0xFF, 0o755, 0b1010, 2j
flags = [None, True, False, ...]
ok = ratio > 1 and not (mask is None) or 3 in [1, 2, 3]'''),

    ("Strings", [
        (['"Tokyo"', 'b"', '"done"'], "#9ece6a", "", "string (b prefix: storage.type.string, #bb9af7)"),
        (['f"Hello {name!r:>10}, {len(name)} letters\\n"'], "#d0f0c0", "",
         "whole f-string: prefix, text, braces, format spec (Tea Green); expressions inside keep their colors"),
        (['r"C:\\Users\\night"', 'R"C:\\Users\\night"'], "#9ab973", "", "raw strings (Muted Olive)"),
        (['r"^(?P<word>[A-Z]\\w+)\\s+\\d{2,4}$"'], "#9ab973", "",
         "raw string as regex: body Muted Olive, regex operators keep their own colors"),
        (["\\x41", "\\x42"], "#89ddff", "", "constant.character.escape"),
    ], '''name = "Tokyo"
greeting = f"Hello {name!r:>10}, {len(name)} letters\\n"
raw_regex_scoped = r"C:\\Users\\night"
raw_plain = R"C:\\Users\\night"
data = b"\\x41\\x42"
pattern = regex.compile(r"^(?P<word>[A-Z]\\w+)\\s+\\d{2,4}$")
print(greeting, raw_regex_scoped == raw_plain, data, pattern.match("Tokyo 2026"), "done")'''),

    ("Comments & docstrings", [
        (["# A regular comment", "# type: int"], "#51597d", ITALIC, "comment"),
        (["TODO", "FIXME", "XXX"], "#e0af68", BOLD, "keyword.codetag"),
        (['"""Triple-quoted docstring.', 'r"""Raw docstring', "'Single-quoted docstring."],
         "#51597d", ITALIC, "string.quoted.docstring: all docstrings now match"),
    ], '''# A regular comment
# TODO: tag inside a comment; FIXME and XXX too


def documented():
    """Triple-quoted docstring."""


def raw_documented():
    r"""Raw docstring with \\d."""


def single_documented():
    'Single-quoted docstring.'


x = 1  # type: int'''),

    ("Functions & parameters", [
        (["def", "lambda", "return"], "#bb9af7", "", "storage.type.function / keyword"),
        (["greet"], "#7aa2f7", "", "semantic function (declaration and call)"),
        (["who:", "*args", "mark:", "**kwargs"], "#e0af68", "", "semantic parameter.declaration"),
        (["{who}", "{mark}"], "#a9b1d6", "", "semantic parameter (use inside the body; plain text as in Tokyo Night)"),
        (["mark=", "sep="], "#cab094", "", "semantic parameter.keywordArgument"),
        (["result"], "#c0caf5", "", "semantic variable (declaration and use)"),
        (["len", "print", "sorted", "str", "int", "object"], "#0db9d7", "", "semantic *.builtin"),
        (["->", ":"], "#89ddff", "", "punctuation"),
    ], '''def greet(who: str, *args: int, mark: str = "!", **kwargs: object) -> str:
    result = f"Hi {who}{mark}"
    return result


square = lambda n: n * n
print(greet("Tokyo", 1, 2, mark="?"), len("abc"), sorted([3, 1, 2]), square(4), sep=" | ")'''),

    ("Classes, methods & decorators", [
        (["class"], "#bb9af7", "", "storage.type.class"),
        (["City", "Megacity"], "#45b1e8", "", "entity.name.type.class (Fresh Sky)"),
        (["@dataclass", "@property", "@classmethod"], "#b59ba8", ITALIC, "semantic *.decorator (Rosy Taupe, subtler)"),
        (["(self)", "(cls)"], "#e0af68", "", "semantic selfParameter.declaration (signature: Tokyo Night orange)"),
        (["self.name", "cls("], "#ca7e89", "", "semantic selfParameter (body: Tokyo Night red, subtler)"),
        (["self.visits = "], "#73daca", "", "semantic property.declaration (visits)"),
        (["self.name", "self.visits"], "#7dcfff", "", "variable.other.property (use)"),
        (["rename", "tokyo"], "#7aa2f7", "", "semantic method"),
        (["__init__", "__repr__"], "#0db9d7", "", "support.function.magic"),
        (["super", "list"], "#0db9d7", "", "semantic *.builtin"),
    ], '''@dataclass
class City:
    name: str
    population: int = 0
    tags: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.name} ({self.population:,})"

    @classmethod
    def tokyo(cls) -> "City":
        return cls("Tokyo", 14_000_000)

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def __repr__(self) -> str:
        return self.label


class Megacity(City):
    def __init__(self, name: str) -> None:
        super().__init__(name, 10_000_000)
        self.visits = 0


osaka = Megacity("Osaka")
osaka.rename("Ōsaka")
print(City.tokyo(), osaka, osaka.visits)'''),

    ("Enums", [
        (["Weather"], "#41a6b5", "", "semantic enum"),
        (["CLEAR", "RAIN", "SNOW"], "#ffcba4", "", "semantic enumMember (Peach Glow)"),
        (["auto"], "#45b1e8", "", "semantic class (Fresh Sky)"),
    ], '''class Weather(Enum):
    CLEAR = auto()
    RAIN = auto()
    SNOW = auto()


tonight = Weather.CLEAR
print(tonight, tonight is Weather.RAIN)'''),

    ("Type hints & generics", [
        (["type"], "#bb9af7", "", "keyword"),
        (["Pair"], "#43b3ae", "", "type alias (Tropical Teal)"),
        (["K", "V", "T"], "#43b3ae", "", "semantic typeParameter (Tropical Teal)"),
        (["tuple", "list"], "#0db9d7", "", "semantic *.builtin"),
    ], '''type Pair[K, V] = tuple[K, V]


def first[T](items: list[T]) -> T | None:
    return items[0] if items else None


counts: Counter[str] = Counter("tokyo")
pair: Pair[str, int] = ("night", 1)
print(first([1, 2, 3]), counts.most_common(1), pair)'''),

    ("Control flow, exceptions & async", [
        (["if", "for", "match", "case", "try", "except", "finally", "raise"], "#bb9af7", "", "keyword.control"),
        (["ValueError", "KeyError"], "#bf4f51", "",
         "support.type.exception (Blushed Brick); Pylance overrides with built-in #0db9d7"),
        (["global"], "#6f00ff", "", "storage.modifier.declaration (Electric Indigo)"),
        (["async", "await"], "#bb9af7", "", "storage.type / keyword"),
        ([":="], "#89ddff", "", "keyword.operator"),
    ], '''counter = 0


def bump() -> None:
    global counter
    counter += 1


def describe(value: object) -> str:
    match value:
        case int(n) if n > 0:
            return "positive int"
        case [first_item, *rest]:
            return f"list starting with {first_item}"
        case _:
            return "something else"


try:
    if (n := len(os.sep)) > 0:
        raise ValueError(f"separator length {n}")
except (ValueError, KeyError) as err:
    print("caught:", err)
finally:
    for _ in range(2):
        bump()


async def fetch() -> str:
    return "done"

print(describe(5), describe([1, 2]), await fetch(), counter)'''),

    ("Deprecated", [
        (["old_api"], "#7aa2f7", STRIKE, "struck through when Pylance flags it"),
    ], '''@deprecated("Use greet() instead")
def old_api() -> None: ...


old_api()'''),
]

READABILITY = [
    ("Electric Indigo", "global", "#6f00ff", "2.5:1",
     "Same contrast as comments; no lighter Coolors color of this hue that doesn't look like the keyword purple."),
    ("Blushed Brick", "ValueError", "#bf4f51", "3.6:1", "Mostly hidden anyway: Pylance colors exceptions as built-ins."),
]


# Tokyo Night as it really looks: TextMate grammar only (no semantic highlighting), from VS Code's tokenizer.
# One group per Tokyo Night rule that wins. Each Tokyo Clear Night row names the rule that colors it;
# rows with the same rule change together.
# (Tokyo Night element, example, color, style, [(Tokyo Clear Night element, example, color, style, rule)])
COMPARISON = [
    ("Plain identifier (no scope)", "os  result", "#a9b1d6", "", [
        ("Module", "os", "#98a288", "", "namespace"),
        ("Variable", "result", "#c0caf5", "", "variable"),
        ("Parameter use", "who", "#a9b1d6", "", "parameter"),
        ("Class use", "Counter", "#45b1e8", "", "class"),
        ("Imported function", "field", "#7aa2f7", "", "function"),
        ("Enum use", "Weather", "#41a6b5", "", "enum"),
        ("Type alias / type parameter", "Pair  T", "#43b3ae", "", "type"),
        ("Built-in as generic", "list[str]", "#0db9d7", "", "builtin"),
        ("Attribute use", ".name", "#7dcfff", "", "property"),
        ("Attribute declaration", ".visits =", "#73daca", "", "property.declaration"),
    ]),
    ("Import keyword", "import  from  as", "#7dcfff", "", [
        ("Import keyword", "import  from  as", "#7dcfff", "", "import"),
    ]),
    ("Keyword", "if  return  TODO", "#bb9af7", "", [
        ("Keyword", "if  return  await", "#bb9af7", "", "keyword"),
        ("TODO tag", "TODO", "#e0af68", BOLD, "todo"),
    ]),
    ("Logical / function keyword", "def  and  >", "#bb9af7", "", [
        ("Logical / function keyword", "def  and  >", "#bb9af7", "", "kwlogical"),
    ]),
    ("Storage type", 'class  b"  f"', "#bb9af7", "", [
        ("class keyword", "class", "#bb9af7", "", "storage"),
        ("String prefix", 'b"  r"', "#bb9af7", "", "storage"),
        ("f-string prefix", 'f"', "#d0f0c0", "", "fstring"),
    ]),
    ("Inherited class", "Megacity(City)", "#bb9af7", "", [
        ("Base class", "City", "#45b1e8", "", "class"),
    ]),
    ("Storage modifier", "global", "#9d7cd8", "", [
        ("global / nonlocal", "global", "#6f00ff", "", "global"),
    ]),
    ("Function name", "greet  @dataclass", "#7aa2f7", "", [
        ("Function / method", "greet", "#7aa2f7", "", "function"),
        ("Class call", "auto()", "#45b1e8", "", "class"),
        ("Decorator", "@dataclass", "#b59ba8", ITALIC, "decorator"),
        ("Deprecated", "old_api", "#7aa2f7", STRIKE, "function"),
    ]),
    ("Class declaration", "City", "#c0caf5", "", [
        ("Class declaration", "City", "#45b1e8", "", "class"),
        ("Enum declaration", "Weather", "#41a6b5", "", "enum"),
    ]),
    ("Parameter", "who:  mark=  self", "#e0af68", "", [
        ("Parameter declaration", "who:", "#e0af68", "", "parameter.declaration"),
        ("Keyword argument", "mark=", "#cab094", "", "keywordArgument"),
        ("self / cls in signature", "self", "#e0af68", "", "self.declaration"),
    ]),
    ("self / cls in body", "self", "#f7768e", "", [
        ("self / cls in body", "self", "#ca7e89", "", "self"),
    ]),
    ("Built-in function", "len  __init__", "#0db9d7", "", [
        ("Built-in function", "len  print", "#0db9d7", "", "builtin"),
        ("Dunder method", "__init__", "#0db9d7", "", "magic"),
    ]),
    ("Built-in type", "str  ValueError", "#0db9d7", "", [
        ("Built-in type", "str  int", "#0db9d7", "", "builtin"),
        ("Exception", "ValueError", "#0db9d7", "", "builtin"),
        ("Built-in decorator", "@property", "#b59ba8", ITALIC, "decorator"),
        ("type statement", "type", "#bb9af7", "", "keyword"),
    ]),
    ("Constant / number", "None  MAX_SIZE  42", "#ff9e64", "", [
        ("Language constant", "None", "#ff9e64", "", "constant"),
        ("Read-only variable", "MAX_SIZE", "#e1a58c", "", "readonly"),
        ("Enum member", "CLEAR", "#ffcba4", "", "enumMember"),
        ("Number", "42", "#f19cbb", "", "number"),
    ]),
    ("Ellipsis", "...", "#e0af68", "", [
        ("Ellipsis", "...", "#e0af68", "", "ellipsis"),
    ]),
    ("String", '"Tokyo"  R"raw"', "#9ece6a", "", [
        ("String", '"Tokyo"', "#9ece6a", "", "string"),
        ("f-string text", 'f"Hello {name}"', "#d0f0c0", "", "fstring"),
        ("Uppercase raw string", 'R"C:\\Users"', "#9ab973", "", "raw"),
        ("Single-quoted / raw docstring", "'Docstring.'", "#51597d", ITALIC, "docstring"),
    ]),
    ("Regex string (lowercase r)", 'r"C:\\Users"', "#b4f9f8", "", [
        ("Raw string", 'r"C:\\Users"', "#9ab973", "", "raw"),
    ]),
    ("Operator / punctuation", "=  ,", "#89ddff", "", [
        ("Operator / punctuation", "=  ,", "#89ddff", "", "operator"),
    ]),
    ("Escape", "\\n", "#89ddff", "", [
        ("Escape", "\\n", "#89ddff", "", "escape"),
    ]),
    ("Comment / triple-quoted docstring", '# note  """Doc."""', "#51597d", ITALIC, [
        ("Comment", "# note", "#51597d", ITALIC, "comment"),
        ("Triple-quoted docstring", '"""Doc."""', "#51597d", ITALIC, "docstring"),
    ]),
]


def comparison_md():
    flat = [(tn, row) for tn in COMPARISON for row in tn[4]]
    rows = []
    for i, ((tn, tn_ex, tn_col, tn_style, ours), (name, ex, col, style, rule)) in enumerate(flat, 1):
        group = f"{tn} {c(tn_col, tn_ex, tn_style)} | {c(tn_col, tn_col)}" if ours[0][4] == rule and ours[0][0] == name else " | "
        shared = ", ".join(str(j) for j, (_, r) in enumerate(flat, 1) if r[4] == rule and j != i) or "—"
        rows.append(f"| {i} | {group} | {name} {c(col, ex, style)} | {c(col, col)} | {shared} |")
    return (
        "# Tokyo Night vs Tokyo Clear Night\n\n"
        "Tokyo Night leaves semantic highlighting off, so it only sees what the TextMate grammar scopes. "
        "Tokyo Clear Night turns it on, so Pylance splits those groups into more element types. "
        "**Shared with** lists the rows colored by the same rule: changing one changes them all.\n\n"
        "| # | Tokyo Night element | Color | Tokyo Clear Night element | Color | Shared with |\n"
        "|---|---|---|---|---|---|\n" + "\n".join(rows)
    )


def legend(title, items):
    rows = "\n".join(f"| {c(col, '  '.join(snips), style)} | <code>{col}</code> | {note} |" for snips, col, style, note in items)
    return f"## {title}\n\n| Element | Color | Source |\n|---|---|---|\n{rows}"


def proposal_md():
    read = "\n".join(f"| {c(col, sample)} {name} | {ratio} | {note} |" for name, sample, col, ratio, note in READABILITY)
    return (
        "# Readability check\n\nContrast against the editor background (<code>#1a1b26</code>); "
        "4.5:1 is the usual minimum for text. Every other color in this notebook is 6:1 or higher, apart from comments, docstrings and inlay hints, which are dim on purpose.\n\n"
        f"| Color | Contrast | Note |\n|---|---|---|\n{read}"
    )


def cell(kind, src, i):
    base = {"cell_type": kind, "id": f"cell-{i}", "metadata": {}, "source": src}
    return base | ({"execution_count": None, "outputs": []} if kind == "code" else {})


cells = [("markdown",
          "# Tokyo Clear Night: Python colors\n\n"
          "Every Python element and the color the theme gives it. Colors marked *semantic* come from Pylance "
          "(<code>semanticHighlighting</code> is on in this theme). Named colors are from "
          "[coolors.co](https://coolors.co/colors). Check any token with "
          "**Developer: Inspect Editor Tokens and Scopes**.\n\n"
          f"Grey hints such as {c('#646e9c', ': float')} after a name are Pylance inlay hints "
          "(<code>editorInlayHint.foreground</code>), not part of the code.")]
for title, items, code in SECTIONS:
    missing = [s for snips, *_ in items for s in snips if s not in code]
    assert not missing, f"{title}: legend snippets not in code: {missing}"
    compile(code, title, "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    cells += [("markdown", legend(title, items)), ("code", code)]
cells.append(("markdown", proposal_md()))
cells.append(("markdown", comparison_md()))

nb = {
    "cells": [cell(k, s, i) for i, (k, s) in enumerate(cells)],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}
out = sys.argv[1] if len(sys.argv) > 1 else "python_demo.ipynb"
with open(out, "w") as f:
    json.dump(nb, f, indent=1)
    f.write("\n")
print(f"{out}: {len(cells)} cells")
