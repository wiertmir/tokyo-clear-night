#!/usr/bin/env python3
"""Generate colors.html: the coolors.co/colors library (coolors_colors.txt) plus this theme's colors, coolors.co style.

coolors_colors.txt lines are hex|name|families (hex digits index FAMILIES), scraped from https://coolors.co/colors.
Theme colors are named after the nearest CSS color (CIELAB distance), so those names are descriptive; needs matplotlib.
"""
import ast
import colorsys
import json
import re
from pathlib import Path

from matplotlib.colors import CSS4_COLORS, to_rgb

ROOT = Path(__file__).parent
FAMILIES = ["Red", "Orange", "Brown", "Yellow", "Green", "Turquoise", "Blue", "Violet", "Pink", "White", "Gray", "Black"]
theme = json.loads((ROOT / "themes/tokyo-clear-night-color-theme.json").read_text())
BG = theme["colors"]["editor.background"]


def lab(h):
    r, g, b = [(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4) for c in to_rgb(h)]
    X, Y, Z = (.4124 * r + .3576 * g + .1805 * b) / .95047, .2126 * r + .7152 * g + .0722 * b, (.0193 * r + .1192 * g + .9505 * b) / 1.089
    f = lambda v: v ** (1 / 3) if v > .008856 else 7.787 * v + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))


NAMES = {n: lab(c) for n, c in CSS4_COLORS.items()}


def name(h):
    L = lab(h)
    n = min(NAMES, key=lambda k: sum((a - b) ** 2 for a, b in zip(L, NAMES[k])))
    return n.capitalize()


def family(h):
    hue, l, s = colorsys.rgb_to_hls(*to_rgb(h))
    if s < .2 or l < .1: return "Neutral"
    hue *= 360
    for top, fam in [(15, "Red"), (45, "Orange"), (70, "Yellow"), (165, "Green"), (195, "Teal"), (255, "Blue"), (290, "Purple"), (335, "Pink"), (361, "Red")]:
        if hue < top: return fam


used = {c.lower() for c in re.findall(r'"foreground": "(#[0-9a-fA-F]{6})', json.dumps(theme))}
# PALETTE lives in make_rust_demo.py; read it without running that script.
palette = next(ast.literal_eval(n.value) for n in ast.parse((ROOT / "make_rust_demo.py").read_text()).body
               if isinstance(n, ast.Assign) and n.targets[0].id == "PALETTE")
colors = []
for line in (ROOT / "coolors_colors.txt").read_text().splitlines():
    h, n, f = line.split("|")
    colors.append({"hex": "#" + h.lower(), "name": n, "fams": [FAMILIES[int(i, 16)] for i in f], "group": "Coolors"})
colors += [{"hex": h, "name": name(h), "fams": [family(h)], "group": "In theme"} for h in sorted(used)]
colors += [{"hex": h, "name": n, "fams": [family(h)], "group": "Unused"} for n, h, _ in palette if h not in used]

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tokyo Clear Night colors</title>
<style>
:root{--bg:#fff;--fg:#1a1b26;--mut:#6b7280;--chip:#eef0f4}
:root[data-theme=dark]{--bg:@BG@;--fg:#c0caf5;--mut:#7982a9;--chip:#24253a}
body{margin:0;background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);padding:16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;z-index:1}
h1{font-size:18px;margin:0 auto 0 0}
button{font:inherit;color:var(--fg);background:var(--chip);border:0;border-radius:999px;padding:6px 14px;cursor:pointer}
button[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;padding:0 16px 32px}
.c{border:0;border-radius:12px;height:130px;padding:12px;text-align:left;display:flex;flex-direction:column;justify-content:space-between;color:var(--t);background:var(--c);box-shadow:inset 0 0 0 1px #8883}
.text .grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}.text .c{background:var(--bg);color:var(--c);height:auto;min-height:64px;box-shadow:inset 0 0 0 1px var(--chip)}.text .c small{color:var(--mut)}.text .c i{color:var(--c)}
.c b{font-weight:600}.c small{opacity:.8}.c i{font:13px ui-monospace,monospace;font-style:normal;opacity:0;transition:opacity .15s}
.c:hover i,.c:focus-visible i{opacity:1}
#toast{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:var(--fg);color:var(--bg);padding:8px 16px;border-radius:8px;opacity:0;transition:opacity .2s;pointer-events:none}
#toast.on{opacity:1}
</style></head><body>
<header><h1>Colors</h1><span id="filters"></span><button id="view">View: Boxes</button> <button id="theme">Theme: Light</button></header>
<div class="grid" id="grid"></div><div id="toast"></div>
<script>
const colors=@DATA@;
const fams=["All",...@FAMS@,"In theme","Unused"];
const $=id=>document.getElementById(id);let cur="All";
const dark=h=>{const [r,g,b]=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));return .299*r+.587*g+.114*b<140};
function draw(){
  $("filters").innerHTML=fams.map(f=>`<button aria-pressed="${f==cur}" data-f="${f}">${f}</button>`).join(" ");
  $("grid").innerHTML=colors.filter(c=>cur=="In theme"||cur=="Unused"?c.group==cur:c.group=="Coolors"&&(cur=="All"||c.fams.includes(cur))).map(c=>
    `<button class="c" data-h="${c.hex}" style="--c:${c.hex};--t:${dark(c.hex)?"#fff":"#111"}"><span><b>${c.name}</b><br><small>${c.fams.join(" · ")}</small></span><i>${c.hex.toUpperCase()}</i></button>`).join("");
}
document.addEventListener("click",e=>{
  const f=e.target.closest("[data-f]");if(f){cur=f.dataset.f;return draw()}
  const c=e.target.closest(".c");if(!c)return;
  navigator.clipboard.writeText(c.dataset.h.toUpperCase());
  $("toast").textContent="Copied "+c.dataset.h.toUpperCase();$("toast").classList.add("on");setTimeout(()=>$("toast").classList.remove("on"),1200);
});
$("view").onclick=()=>{const t=document.documentElement.classList.toggle("text");$("view").textContent="View: "+(t?"Text":"Boxes")};
$("theme").onclick=()=>{const d=document.documentElement,on=d.dataset.theme!="dark";d.dataset.theme=on?"dark":"light";$("theme").textContent="Theme: "+(on?"Tokyo Clear Night":"Light")};
draw();
</script></body></html>"""
(ROOT / "colors.html").write_text(HTML.replace("@BG@", BG).replace("@DATA@", json.dumps(colors)).replace("@FAMS@", json.dumps(FAMILIES)))
print(f"colors.html: {len(colors)} colors")
