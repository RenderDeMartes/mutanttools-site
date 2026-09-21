# Docs generator

These scripts write four pages of mutanttools.com from the **Mutant_Tools source
itself**, so the documentation cannot drift away from the code:

| Page | What it is |
|---|---|
| `/developer/` | The Python developer guide, hand-written prose |
| `/wiki/` | Reference landing page |
| `/wiki/commands/` | Every `mt` method, generated from the AST |
| `/wiki/blocks/` | Every shipped block, generated from the launcher JSONs |
| `/maya-auto-rigger/` | Search landing page, with JSON-LD |

It also writes `llms.txt`, `sitemap.xml` and `robots.txt`, and adds the Auto
Rigger nav item to the pages it does not own.

## Regenerating after a Mutant Tools release

```bash
git clone --depth 1 https://github.com/RenderDeMartes/Mutant_Tools.git /tmp/MT
cd tools
python extract_mt.py /tmp/MT
python build_mtdocs.py
```

Then bump `SHA`, `REPO_DATE` and `MT_VERSION` at the top of `build_mtdocs.py`
so the "generated from" line on `/developer/` stays honest.

The clone is large because of the binaries. To skip them:

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/RenderDeMartes/Mutant_Tools.git /tmp/MT
cd /tmp/MT
git sparse-checkout set --no-cone '/*' \
  '!/Utils/Unreal/MetaHuman/dna_calibration' '!*.png' '!*.ma' '!*.FBX' '!*.dna' '!*.jpg'
```

The build is idempotent - running it twice gives byte-identical output.

## Files

| File | Role |
|---|---|
| `extract_mt.py` | Reads a Mutant_Tools checkout, writes `mt_api.json` and `blocks.json`. Imports no Maya. |
| `build_mtdocs.py` | Orchestrator. Writes the pages, `llms.txt`, the sitemap, and patches the nav. |
| `mt_shell.py` | The page shell and the docs stylesheet |
| `mt_md.py` | Python syntax highlighter and markup helpers |
| `mt_dev.py` | `/developer/` content |
| `mt_wiki.py` | `/wiki/`, `/wiki/commands/`, `/wiki/blocks/` content |
| `mt_seo.py` | `/maya-auto-rigger/` content and its JSON-LD |
| `shell_*.html` | The Astra chrome, lifted verbatim from a WordPress-era page |
| `mt_api.json`, `blocks.json`, `curves.json` | Extracted data, committed so a build needs no checkout |

## Why not Sphinx

The repo carries a `Docs/` Sphinx setup, and its output is still served at
`/docs/_build/html/`. It cannot be rebuilt outside the original author's
machine: `Docs/conf.py` hardcodes `C://Users//Esteban//Documents//maya//2022//...`
and a Maya 2022 site-packages path, and autodoc has to import `Mutant_Tools`,
which means importing `maya.cmds`. The mock objects in `conf.py` paper over some
of that, but the result is one thin stub page per module with no signatures worth
reading and no search.

Parsing the AST instead needs nothing but Python. It also yields better output:
real default values, line numbers that link back to the source, full docstrings,
and every block's options in one searchable page.

The old build stays online and is still linked from `/wiki/`, so existing
bookmarks keep working.

## Notes

- `tools/` is deliberately **not** in `.cpanel.yml`, so it never deploys.
- The shell fragments carry the Developer page's "current page" nav markers.
  `mt_shell` strips them on import and `page(nav_current=...)` re-applies them,
  otherwise every generated page would highlight Developer in the menu.
- Page weight looks alarming (the commands page is ~430 KB) but ~95 KB of that
  is Astra's inline CSS, present on every page of the site, and the server
  gzips: the largest page is 64 KB over the wire.
