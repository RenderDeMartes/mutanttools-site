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
| `/rigger/`, `/learn/`, `/free-assets/`, `/contact/` | The former WordPress pages, rebuilt on the same components |
| `/web-to-rig/` | Web to Rig, a browser tool: place a skeleton on a character, download a folder that Maya turns into a full Mutant Tools rig |

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
| `mt_shell.py` | The page shell; links `assets/css/mt-ui.css` with a content hash |
| `mt_md.py` | Python syntax highlighter and the component builders (hero, card, media card, button, cta, note, table) |
| `mt_pages.py` | `/rigger/`, `/learn/`, `/free-assets/`, `/contact/` content |
| `mt_dev.py` | `/developer/` content |
| `mt_wiki.py` | `/wiki/`, `/wiki/commands/`, `/wiki/blocks/` content |
| `mt_seo.py` | `/maya-auto-rigger/` content and its JSON-LD |
| `mt_placer.py` | `/web-to-rig/`, the frame for `assets/js/joint-placer.js` (three.js, pinned, from jsDelivr), and the walkthrough of what happens in Maya |
| `joint_placer_format.md` | What `/web-to-rig/` downloads, for WebToRig in Mutant Tools (`UI/WebToRig`) |
| `assets/models/` | Web to Rig's CC0 example character and test animations, by Quaternius (see `CREDITS.txt` there), and the Manny reference skeleton |
| `assets/maya/Drag_into_Maya.py` | Goes in every Web to Rig download: installs Mutant Tools if needed, then opens WebToRig on the folder |
| `shell_*.html` | The Astra chrome, lifted verbatim from a WordPress-era page |
| `mt_api.json`, `blocks.json`, `curves.json` | Extracted data, committed so a build needs no checkout |

## One look for every page

Every page is built from the components in `mt_md.py` and styled by one file,
`assets/css/mt-ui.css`, which follows the Mutant Tools brand kit (Ink and
Graphite grounds, the site's orange for the one action per screen, Archivo Black /
Manrope / IBM Plex Mono, the UI icons in `assets/icons/`). Change the look there,
then rebuild: the shell links the stylesheet as `mt-ui.css?v=<hash>`, and CSS is
cached for a year, so a CSS edit without a rebuild never reaches returning visitors.

The homepage links the same file. Its four-panel hero keeps its own inline
styles; only the section `mt_home.py` appends below the hero uses the components.

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

## Tuning Web to Rig's auto placement

Open `/web-to-rig/?debug` and the page puts its state on `window.__placer`
(`S`, `autoPlace`, `loadBuffer`, `rebuild`). The example character carries its
own hand-placed skeleton, so after a placement each of our joints can be
measured against the matching bone (`pelvis`, `upperarm_l` ...) in the console.
On Quaternius' male and female base characters the auto placement lands within
about 2 cm on average of their skeletons, worst joint about 4 cm (the shoulders).
The spine's inner joints follow the Mutant Tools template's spacing, so they
sit higher than Unreal-style spine_02 and spine_03 by design.

## Notes

- `tools/` is deliberately **not** in `.cpanel.yml`, so it never deploys.
- The shell fragments carry the Developer page's "current page" nav markers.
  `mt_shell` strips them on import and `page(nav_current=...)` re-applies them,
  otherwise every generated page would highlight Developer in the menu.
- Page weight looks alarming (the commands page is ~430 KB) but ~95 KB of that
  is Astra's inline CSS, present on every page of the site, and the server
  gzips: the largest page is 64 KB over the wire.
