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
        (["os", "re", "collections", "dataclasses"], "#91a3b0", "", "semantic module (Cool Steel)"),
        (["Counter", "Enum"], "#45b1e8", "", "semantic class (Fresh Sky)"),
        (["dataclass", "field"], "#7aa2f7", "", "semantic function"),
    ], '''import os
import re as regex
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from warnings import deprecated'''),

    ("Constants, numbers & operators", [
        (["MAX_SIZE"], "#ff9e64", "", "semantic variable.readonly; plain #c0caf5 if Pylance doesn't mark it read-only"),
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
        (["{who}", "{mark}"], "#d9d4cd", "", "semantic parameter (use inside the body)"),
        (["mark=", "sep="], "#d9d4cd", "", "semantic parameter.keywordArgument"),
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
        (["@dataclass", "@property", "@classmethod"], "#bc8f8f", ITALIC, "semantic *.decorator (Rosy Taupe)"),
        (["self", "cls"], "#e0af68", "", "selfParameter / clsParameter → variable.parameter (Tokyo Night)"),
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
