// Usage: node rust_tokens.js <crate dir with src/main.rs> <theme.json>... > tokens.json
// Colors every char of src/main.rs the way VS Code would: TextMate scopes (built-in Rust grammar), then rust-analyzer
// semantic tokens on top when the theme enables semanticHighlighting. Both parts follow VS Code's resolution rules.
const fs = require("fs"), path = require("path"), cp = require("child_process"), os = require("os");
const NM = process.env.VSC_NM, EXT = process.env.RA_EXT, VSC = "/usr/share/code/resources/app/extensions/rust/syntaxes/rust.tmLanguage.json";
const tm = require(NM + "/vscode-textmate"), onig = require(NM + "/vscode-oniguruma");

const jsonc = t => JSON.parse(t.replace(/("(?:\\.|[^"\\])*")|\/\/[^\n]*|\/\*[\s\S]*?\*\//g, (m, s) => s || "")
  .replace(/("(?:\\.|[^"\\])*")|,(\s*[}\]])/g, (m, s, b) => s || b));

// ---------- TextMate theme matching ----------
const FS = s => ({ bold: /bold/.test(s), italic: /italic/.test(s), underline: /underline/.test(s), strikethrough: /strikethrough/.test(s) });
function loadTheme(file) {
  const t = jsonc(fs.readFileSync(file, "utf8")), rules = [];
  let def = { fg: t.colors["editor.foreground"] };
  for (const r of t.tokenColors) {
    const st = { fg: r.settings.foreground, fs: r.settings.fontStyle === undefined ? undefined : FS(r.settings.fontStyle) };
    if (!r.scope) { def = { ...def, ...(st.fg && { fg: st.fg }) }; continue; }
    const sc = Array.isArray(r.scope) ? r.scope : r.scope.split(",");
    for (const s of sc) { const sel = s.trim(); if (sel && !/ - /.test(sel)) rules.push({ parts: sel.split(/\s+/), st, i: rules.length }); }
  }
  const sem = [];
  if (t.semanticHighlighting) for (const [sel, v] of Object.entries(t.semanticTokenColors || {})) {
    const o = typeof v === "string" ? { foreground: v } : v;
    sem.push({ ...parseSel(sel), st: { fg: o.foreground, fs: ["bold", "italic", "underline", "strikethrough"].some(k => k in o) ? { bold: o.bold, italic: o.italic, underline: o.underline, strikethrough: o.strikethrough } : undefined } });
  }
  return { def, rules, sem, semOn: !!t.semanticHighlighting };
}
const pre = (sel, sc) => sc === sel || sc.startsWith(sel + ".");
// style of a scope stack: per scope from root to leaf, the most specific matching rule sets each property it defines
function tmStyle(theme, stack, useDefault = true) {
  let fg = useDefault ? theme.def.fg : undefined, fsx;
  for (let d = 0; d < stack.length; d++) {
    let bf, bs;
    for (const r of theme.rules) {
      const last = r.parts.at(-1); if (!pre(last, stack[d])) continue;
      let p = r.parts.length - 2, ok = true;
      for (let k = d - 1; p >= 0 && k >= 0; k--) if (pre(r.parts[p], stack[k])) p--;
      if (p >= 0) ok = false; if (!ok) continue;
      const key = [last.split(".").length, r.parts.length, r.i];
      const better = o => !o || key[0] > o.key[0] || (key[0] == o.key[0] && (key[1] > o.key[1] || (key[1] == o.key[1] && key[2] > o.key[2])));
      if (r.st.fg && better(bf)) bf = { key, v: r.st.fg };
      if (r.st.fs && better(bs)) bs = { key, v: r.st.fs };
    }
    if (bf) fg = bf.v; if (bs) fsx = bs.v;
  }
  return { fg, fs: fsx };
}

// ---------- semantic tokens ----------
const SUPER = { method: "member", member: "function", macro: "function", struct: "type", class: "type", interface: "type", enum: "type", typeParameter: "type", parameter: "variable", property: "variable", enumMember: "variable", event: "variable", decorator: "variable" };
function parseSel(s) { const [t, ...m] = s.split(":")[0].split("."); return { type: t, mods: m }; }
function chain(type, extra) { const c = [type]; while ((extra[c.at(-1)] || SUPER[c.at(-1)])) c.push(extra[c.at(-1)] || SUPER[c.at(-1)]); return c; }
function score(sel, type, mods, ch) {
  if (!sel.mods.every(m => mods.includes(m))) return -1;
  let s = sel.mods.length * 100;
  if (sel.type === "*") return s + 1;
  const k = ch.indexOf(sel.type); return k < 0 ? -1 : s + 2 + (ch.length - k);
}
// VS Code's default token -> TextMate scope mapping, plus the rust-analyzer extension's semanticTokenScopes
const DEFAULTS = {
  comment: ["comment"], string: ["string"], keyword: ["keyword.control"], number: ["constant.numeric"], regexp: ["constant.regexp"],
  operator: ["keyword.operator"], namespace: ["entity.name.namespace"], type: ["entity.name.type", "support.type"],
  struct: ["entity.name.type.struct"], class: ["entity.name.type.class", "support.class"], interface: ["entity.name.type.interface"],
  enum: ["entity.name.type.enum"], typeParameter: ["entity.name.type.parameter"], function: ["entity.name.function", "support.function"],
  member: ["entity.name.function.member", "support.function"], macro: ["entity.name.function.preprocessor"],
  variable: ["variable.other.readwrite", "entity.name.variable"], parameter: ["variable.parameter"], property: ["variable.other.property"],
  enumMember: ["variable.other.enummember"], event: ["variable.other.event"], decorator: ["entity.name.decorator", "meta.decorator"],
  label: ["entity.name.label"], "variable.readonly": ["variable.other.constant"],
};
function semStyle(theme, tok, ra) {
  const ch = chain(tok.type, ra.supers), res = { fg: undefined, fs: {} };
  const sc = { fg: -1, b: -1, i: -1, u: -1, s: -1 };
  const apply = (st, score) => {
    if (st.fg && score >= sc.fg) { res.fg = st.fg; sc.fg = score; }
    if (st.fs) for (const [k, key] of [["bold", "b"], ["italic", "i"], ["underline", "u"], ["strikethrough", "s"]])
      if (st.fs[k] !== undefined && score >= sc[key]) { res.fs[k] = st.fs[k]; sc[key] = score; }
  };
  for (const r of theme.sem) { const s = score(r, tok.type, tok.mods, ch); if (s >= 0) apply(r.st, s); }
  // theme rules beat the defaults property by property
  const themed = { ...sc };
  const defs = [];
  for (const [sel, scopes] of [...Object.entries(DEFAULTS), ...Object.entries(ra.scopes)]) {
    const s = score(parseSel(sel), tok.type, tok.mods, ch); if (s < 0) continue;
    for (const alt of scopes) { const st = tmStyle(theme, [ "source.rust", ...(Array.isArray(alt) ? alt : [alt]) ], false); if (st.fg || st.fs) { defs.push([s, st]); break; } }
  }
  defs.sort((a, b) => a[0] - b[0]);
  const keep = { ...res, fs: { ...res.fs } };
  const tmp = { fg: res.fg, fs: res.fs };
  for (const [s, st] of defs) {
    if (st.fg && themed.fg < 0) tmp.fg = st.fg;
    if (st.fs) for (const [k, key] of [["bold", "b"], ["italic", "i"], ["underline", "u"], ["strikethrough", "s"]]) if (st.fs[k] !== undefined && themed[key] < 0) tmp.fs[k] = st.fs[k];
  }
  return tmp;
}

// ---------- rust-analyzer ----------
async function semanticTokens(crate) {
  const server = cp.spawn(path.join(EXT, "server/rust-analyzer"), [], { cwd: crate });
  let buf = Buffer.alloc(0), id = 0; const pend = new Map();
  server.stdout.on("data", d => {
    buf = Buffer.concat([buf, d]);
    for (;;) {
      const h = buf.indexOf("\r\n\r\n"); if (h < 0) return;
      const len = +/Content-Length: (\d+)/.exec(buf.slice(0, h).toString())[1];
      if (buf.length < h + 4 + len) return;
      const m = JSON.parse(buf.slice(h + 4, h + 4 + len)); buf = buf.slice(h + 4 + len);
      if (m.id !== undefined && m.method) send({ id: m.id, result: m.method === "workspace/configuration" ? m.params.items.map(() => null) : null });
      else if (m.id !== undefined && pend.has(m.id)) pend.get(m.id)(m);
    }
  });
  const send = o => { const s = JSON.stringify({ jsonrpc: "2.0", ...o }); server.stdin.write(`Content-Length: ${Buffer.byteLength(s)}\r\n\r\n${s}`); };
  const req = (method, params) => new Promise(r => { const i = ++id; pend.set(i, r); send({ id: i, method, params }); });
  const root = "file://" + crate, uri = root + "/src/main.rs";
  const init = await req("initialize", { processId: process.pid, rootUri: root, workspaceFolders: [{ uri: root, name: "demo" }], capabilities: {
    workspace: { configuration: true }, textDocument: { semanticTokens: { requests: { full: true }, tokenTypes: [], tokenModifiers: [], formats: ["relative"], multilineTokenSupport: false } } } });
  send({ method: "initialized", params: {} });
  send({ method: "textDocument/didOpen", params: { textDocument: { uri, languageId: "rust", version: 1, text: fs.readFileSync(crate + "/src/main.rs", "utf8") } } });
  const legend = init.result.capabilities.semanticTokensProvider.legend;
  let prev, data;
  for (let i = 0; i < 40; i++) {            // analysis is lazy: wait until two answers in a row agree
    await new Promise(r => setTimeout(r, 1500));
    const r = await req("textDocument/semanticTokens/full", { textDocument: { uri } });
    data = r.result && r.result.data; const j = JSON.stringify(data);
    if (data && j === prev && i > 3) break; prev = j;
  }
  server.kill();
  return { data, legend };
}

(async () => {
  const [crate, ...themeFiles] = process.argv.slice(2);
  const pkg = JSON.parse(fs.readFileSync(EXT + "/package.json")).contributes;
  const ra = { supers: Object.fromEntries(pkg.semanticTokenTypes.filter(t => t.superType).map(t => [t.id, t.superType])),
    scopes: pkg.semanticTokenScopes.find(s => s.language === "rust").scopes };
  const text = fs.readFileSync(crate + "/src/main.rs", "utf8"), lines = text.split("\n");
  // TextMate
  await onig.loadWASM(fs.readFileSync(NM + "/vscode-oniguruma/release/onig.wasm").buffer);
  const reg = new tm.Registry({ onigLib: Promise.resolve({ createOnigScanner: s => new onig.OnigScanner(s), createOnigString: s => new onig.OnigString(s) }),
    loadGrammar: async () => tm.parseRawGrammar(fs.readFileSync(VSC, "utf8"), VSC) });
  const g = await reg.loadGrammar("source.rust");
  const scopes = [], lineStart = []; let state = tm.INITIAL, off = 0;
  for (const l of lines) {
    lineStart.push(off); const r = g.tokenizeLine(l, state); state = r.ruleStack;
    for (const t of r.tokens) for (let c = t.startIndex; c < Math.min(t.endIndex, l.length); c++) scopes[off + c] = t.scopes;
    off += l.length + 1;
  }
  // semantic
  const { data, legend } = await semanticTokens(path.resolve(crate));
  const toks = []; let line = 0, col = 0;
  for (let i = 0; i < data.length; i += 5) {
    line += data[i]; col = data[i] ? data[i + 1] : col + data[i + 1];
    const mods = legend.tokenModifiers.filter((_, b) => data[i + 4] & (1 << b));
    toks.push({ start: lineStart[line] + col, len: data[i + 2], type: legend.tokenTypes[data[i + 3]], mods });
  }
  const semAt = []; for (const t of toks) for (let c = 0; c < t.len; c++) semAt[t.start + c] = t;
  const out = { text, tokens: toks, themes: {} };
  for (const f of themeFiles) {
    const th = loadTheme(f), chars = [];
    for (let i = 0; i < text.length; i++) {
      let st = scopes[i] ? tmStyle(th, scopes[i]) : { fg: th.def.fg }, fgc = st.fg, f2 = { ...(st.fs || {}) };
      const tok = th.semOn && semAt[i];
      if (tok) { const s = semStyle(th, tok, ra); if (s.fg) fgc = s.fg; Object.assign(f2, Object.fromEntries(Object.entries(s.fs).filter(([, v]) => v !== undefined))); }
      chars.push([fgc, Object.keys(f2).filter(k => f2[k]).join("+")]);
    }
    out.themes[path.basename(f)] = chars;
  }
  out.scopes = scopes.map(s => s && s.slice(1));
  console.log(JSON.stringify(out));
})();
