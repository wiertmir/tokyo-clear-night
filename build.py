#!/usr/bin/env python3
"""Build Tokyo Clear Night = Tokyo Night + overrides.jsonc."""
import json
import re
from pathlib import Path

HOME = Path.home()
SRC = next(HOME.glob(".vscode/extensions/enkia.tokyo-night-*/themes/tokyo-night-color-theme.json"))
OVERRIDES = Path(__file__).parent / "overrides.jsonc"
OUT = Path(__file__).parent / "themes/tokyo-clear-night-color-theme.json"


def load_jsonc(text):
    # Drop // and /* */ comments outside strings, then trailing commas.
    text = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*.*?\*/', lambda m: m.group(1) or "", text, flags=re.S)
    text = re.sub(r'("(?:\\.|[^"\\])*")|,(\s*[}\]])', lambda m: m.group(1) or m.group(2), text)
    return json.loads(text)


def build():
    theme = load_jsonc(SRC.read_text())
    over = load_jsonc(OVERRIDES.read_text())
    theme["colors"].update(over.get("colors", {}))
    theme["tokenColors"] += over.get("tokenColors", [])
    theme.setdefault("semanticTokenColors", {}).update(over.get("semanticTokenColors", {}))
    if "semanticHighlighting" in over:
        theme["semanticHighlighting"] = over["semanticHighlighting"]

    theme["name"] = "Tokyo Clear Night"
    theme["author"] = "wiertmir"
    theme["maintainers"] = ["wiertmir"]
    theme["description"] = "Based on Tokyo Night by Enkia (MIT)"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(theme, indent=4) + "\n")
    return theme


if __name__ == "__main__":
    assert load_jsonc('{"a": "x//y", /* c */ "b": [1,], // z\n}') == {"a": "x//y", "b": [1]}
    t = build()
    print(f"{OUT}: {len(t['colors'])} colors, {len(t['tokenColors'])} token rules")
