# Tokyo Clear Night

[Tokyo Night](https://github.com/tokyo-night/tokyo-night-vscode-theme) with brighter UI chrome: readable sidebar, tabs, menus and breadcrumbs, teal (`#73daca`) highlights, clearer list selections, and lighter notebook pages behind darker cells.

![Tokyo Clear Night: a Jupyter notebook with code, a DataFrame and a traceback](images/screenshot.png)

## Building

The theme is generated from the installed Tokyo Night extension plus `overrides.jsonc`:

```sh
python3 build.py
npx @vscode/vsce package
```

`python3 make_python_demo.py` regenerates `python_demo.ipynb`, a notebook showing every Python element with its color. Update its tables when you change Python colors in `overrides.jsonc`.

## License

MIT. Based on Tokyo Night by Enkia (MIT).
