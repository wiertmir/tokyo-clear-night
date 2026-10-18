# Tokyo Clear Night

[Tokyo Night](https://github.com/tokyo-night/tokyo-night-vscode-theme) with brighter UI chrome: readable sidebar, tabs, menus and breadcrumbs, teal (`#73daca`) highlights, clearer list selections, and lighter notebook pages behind darker cells.

## Building

The theme is generated from the installed Tokyo Night extension plus `overrides.jsonc`:

```sh
python3 build.py
npx @vscode/vsce package
```

## License

MIT. Based on Tokyo Night by Enkia (MIT).
