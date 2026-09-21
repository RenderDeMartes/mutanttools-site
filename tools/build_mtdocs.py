# -*- coding: utf-8 -*-
"""Generate the mutanttools.com developer docs, wiki and auto-rigger landing page.

    cd tools
    python extract_mt.py <path-to-Mutant_Tools-checkout>   # refresh the data
    python build_mtdocs.py                                 # write the pages

Writes into this folder's parent, the site root. See tools/README.md.
"""
from __future__ import absolute_import
import io, json, os, re, collections

import mt_shell as shell
import mt_md as m
import mt_dev, mt_wiki, mt_seo, mt_cluster, mt_home

SCRATCH = os.path.dirname(os.path.abspath(__file__))
SITE = shell.SITE

SHA = "2dc3eae"
REPO_DATE = "18 September 2026"
MT_VERSION = "1.6"


def load():
    api = json.load(io.open(os.path.join(SCRATCH, "mt_api.json"), encoding="utf-8"))
    cats = json.load(io.open(os.path.join(SCRATCH, "blocks.json"), encoding="utf-8"),
                     object_pairs_hook=collections.OrderedDict)
    curves = json.load(io.open(os.path.join(SCRATCH, "curves.json"),
                               encoding="utf-8"))
    methods = 0
    for cls in ("Tools_class", "Kinematics_class", "Modules_class", "Mutant"):
        methods += len([x for x in api[cls]["methods"] if not x[0].startswith("_")])
    stats = {
        "methods": methods,
        "blocks": sum(len(v) for v in cats.values()),
        "categories": len(cats),
        "curves": len(curves),
        "curve_names": sorted(curves.keys()),
        "sha": SHA,
        "date": REPO_DATE,
        "version": MT_VERSION,
    }
    return api, cats, stats


# ---------------------------------------------------------------- llms.txt
def llms_txt(stats):
    return """# Mutant Tools

> A free, block-based auto rigger and modular rigging framework for Autodesk Maya.
> Built by Blue Tape Rigging. Source is public: https://github.com/RenderDeMartes/Mutant_Tools

Mutant Tools rigs characters, creatures, vehicles and props in Maya. A rig is a stack of
independent "blocks", each owning one piece of anatomy. Blocks and their guides are the
source of truth; the rig is regenerated output, so rebuilding is routine rather than risky.

Version %(version)s. Maya 2022+. Python 2 and 3 compatible. Free, no licence server.

## Core API

Every script starts the same way:

    from maya import cmds
    from Mutant_Tools.Utils.Rigging import main_mutant
    mt = main_mutant.Mutant()
    nc, curve_data, setup = mt.import_configs()

`mt` exposes %(methods)d public methods, inherited down a chain:
Mutant -> Modules_class (blocks, guides, base rig) -> Kinematics_class (FK/IK, twist,
ribbons) -> Tools_class (controls, attributes, colour, nodes, JSON).

`nc` is naming conventions, `setup` is rig defaults, `curve_data` is %(curves)d control
shapes. All three are JSON under Mutant_Tools/config/. Never hardcode a suffix that exists
in `nc`.

## Block model

- A block is a Maya dagContainer named <Name>_Block, parented under a Mutant_Build group.
- Its options live on a sibling `network` node named <Name>_Config.
- A block on disk is a folder under Blocks/<category>/ holding a launcher JSON, a versioned
  JSON and a versioned exec_*.py with create_<block>_block() and build_<block>_block().
- create_ makes the block, config and guides. build_ reads the config and produces rig.
- The builder runs blocks in OUTLINER ORDER, selecting each block before each phase:
  import -> precode -> build -> postcode. Build functions take no arguments; they read
  cmds.ls(sl=True).
- The return value of build_ is kept in a recipe dict keyed by block name.

## Block JSON attribute suffixes

_string -> string attribute. _enum -> enum, colon separated. _bool -> boolean.
_float -> NOT a float: an INTEGER clamped between 1 and 20.
Type detection is a substring test in the order string, enum, float, bool, so avoid putting
a type word inside a descriptive attribute name.

## Hard rules when writing or modifying block code

1. Entry point is always `mt = main_mutant.Mutant()`.
2. Every create_ and build_ starts with `nc, curve_data, setup = mt.import_configs()`.
3. Every build_ then calls `mt.check_is_there_is_base()`.
4. Guard every scene operation with cmds.objExists and cmds.attributeQuery(..., exists=True).
5. Never assume selection order or count without validating.
6. Repeated helper groups need mt.root_grp(input=node, custom=True, custom_name='Unique').
   root_grp reparents its input, so refresh stale DAG paths afterwards.
7. When rebuilding constraints, cache type and targets and restore with mo=True.
8. New block attributes must be read behind attributeQuery so scenes saved before the attr
   existed still rebuild. Fall back to the JSON default.
9. Block versioning is mandatory. Copy exec/json to the next _vNNN, edit only the new files,
   repoint the launcher JSON, and never delete or rewrite an old version.
10. Prefer nc/setup values over hardcoded names. cmds.warning for recoverable issues,
    print for milestones. Make minimal edits; do not refactor unrelated code.

## Pages

- [Developer guide](https://mutanttools.com/developer/): the full Python guide - mt object,
  configs, block anatomy, build lifecycle, a complete worked block, traps, pipeline use.
- [Command reference](https://mutanttools.com/wiki/commands/): all %(methods)d mt methods with
  real signatures, generated from source.
- [Block catalogue](https://mutanttools.com/wiki/blocks/): all %(blocks)d shipped blocks with
  their config attributes and build commands.
- [Wiki index](https://mutanttools.com/wiki/): reference landing page.
- [Maya auto rigger](https://mutanttools.com/maya-auto-rigger/): what the tool does, how
  block-based rigging differs, requirements, FAQ.
- [For riggers](https://mutanttools.com/rigger/): the artist-facing tour.
- [Learn](https://mutanttools.com/learn/): workflow walkthroughs.
- [Free assets](https://mutanttools.com/free-assets/): downloadable rigs and tools.
- [Contact](https://mutanttools.com/contact/)

## In-repo AI documentation

- Docs/AI_MT_COMMAND_RULES.md: the rules above in full, with a copy/paste initial prompt.
- Docs/AI_MT_COMMAND_TUTORIAL.md: 60 worked examples of the block patterns.
- .gemini.md: workspace context for assistants.

Generated from RenderDeMartes/Mutant_Tools at %(sha)s.
""" % stats


# ------------------------------------------------------------------ sitemap
PAGES = [
    ("/", "weekly"),
    ("/maya-auto-rigger/", "monthly"),
    ("/free-maya-rigging-tools/", "monthly"),
    ("/maya-facial-rigging/", "monthly"),
    ("/maya-animal-rigging/", "monthly"),
    ("/game-character-rigging-maya/", "monthly"),
    ("/rigger/", "monthly"),
    ("/developer/", "monthly"),
    ("/wiki/", "monthly"),
    ("/wiki/commands/", "monthly"),
    ("/wiki/blocks/", "monthly"),
    ("/learn/", "monthly"),
    ("/free-assets/", "monthly"),
    ("/contact/", "yearly"),
]


CLUSTER = ("/maya-auto-rigger/", "/free-maya-rigging-tools/", "/maya-facial-rigging/",
           "/maya-animal-rigging/", "/game-character-rigging-maya/")


def sitemap():
    rows = []
    for path, freq in PAGES:
        pri = "1.0" if path == "/" else ("0.9" if path in CLUSTER or path == "/developer/" else "0.7")
        rows.append("  <url><loc>https://mutanttools.com%s</loc>"
                    "<changefreq>%s</changefreq><priority>%s</priority></url>" % (path, freq, pri))
    rows.append("  <url><loc>https://mutanttools.com/docs/_build/html/index.html</loc>"
                "<changefreq>yearly</changefreq><priority>0.3</priority></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


# Pages this script writes in full. fix_nav leaves them alone.
GENERATED = {
    "developer/index.html",
    "wiki/index.html",
    "wiki/commands/index.html",
    "wiki/blocks/index.html",
    "maya-auto-rigger/index.html",
    "index.html",
} | set("%s/index.html" % slug for slug, _f, _t, _d in mt_cluster.PAGES)


# ------------------------------------------------------------- nav repair
def fix_nav():
    """Bring the nav on the pages this script does not regenerate up to date.

    Two edits: point the Wiki item at the new wiki, and add the Auto Rigger item.
    Only the nav's Wiki link is rewritten - it carries `class="menu-link"`. A
    blanket replace would also rewrite the wiki index's deliberate link to the
    old Sphinx build, which exists so old bookmarks still land somewhere.
    """
    nav_link = re.compile(r'href="/docs/_build/html/index\.html"(?=[^>]*class="menu-link")')
    touched = []
    for root, _, files in os.walk(SITE):
        if os.sep + "assets" in root:
            continue
        for f in files:
            if f != "index.html":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SITE).replace(os.sep, "/")
            if rel in GENERATED:
                continue          # rewritten from scratch below
            s = io.open(p, encoding="utf-8").read()
            new = shell.add_auto_rigger(nav_link.sub('href="/wiki/"', s))
            if new == s:
                continue
            io.open(p, "w", encoding="utf-8", newline="\n").write(new)
            touched.append(os.path.relpath(p, SITE))
    return touched


# ---------------------------------------------------------------------- run
def main():
    api, cats, stats = load()
    print("source: %d mt methods, %d blocks in %d categories, %d curves"
          % (stats["methods"], stats["blocks"], stats["categories"], stats["curves"]))

    touched = fix_nav()
    print("nav patched on %d existing pages: %s" % (len(touched), ", ".join(touched)))

    written = []

    # /developer/
    html = shell.page(
        "Mutant Tools for Python Developers - Block API, mt Commands & Maya Rigging",
        "Write Maya rigging blocks with Mutant Tools. The full mt Python API, block anatomy, "
        "the build lifecycle, a complete worked example, and the traps to avoid.",
        "https://mutanttools.com/developer/",
        mt_dev.build(stats), nav_current="/developer/")
    written.append(shell.write("developer/index.html", html))

    # /wiki/
    written.append(shell.write("wiki/index.html", shell.page(
        "Mutant Tools Wiki - mt Command & Block Reference for Maya",
        "Searchable reference for Mutant Tools: every mt command with its real signature and "
        "every shipped rigging block with its options.",
        "https://mutanttools.com/wiki/",
        mt_wiki.index(stats), nav_current="/wiki/")))

    written.append(shell.write("wiki/commands/index.html", shell.page(
        "mt Command Reference - Mutant Tools Python API for Maya",
        "All %d public methods on the Mutant Tools mt object, with full signatures and defaults, "
        "generated from the source." % stats["methods"],
        "https://mutanttools.com/wiki/commands/",
        mt_wiki.commands(api), nav_current="/wiki/")))

    written.append(shell.write("wiki/blocks/index.html", shell.page(
        "Block Catalogue - Every Mutant Tools Rigging Block for Maya",
        "All %d Mutant Tools blocks for Maya: biped, facial, animal, vehicle, prop and game "
        "modules, with the options each one exposes." % stats["blocks"],
        "https://mutanttools.com/wiki/blocks/",
        mt_wiki.blocks(cats), nav_current="/wiki/")))

    # /maya-auto-rigger/
    body, ld = mt_seo.build(stats)
    written.append(shell.write("maya-auto-rigger/index.html", shell.page(
        "Maya Auto Rigger - Free Modular Auto Rigging for Maya | Mutant Tools",
        "Mutant Tools is a free, open-source auto rigger for Autodesk Maya. %d block-based "
        "modules for biped, facial, animal, vehicle and game rigs, with a full Python API."
        % stats["blocks"],
        "https://mutanttools.com/maya-auto-rigger/",
        body, extra_head=ld, nav_current="/maya-auto-rigger/")))

    # the topic cluster around /maya-auto-rigger/
    for slug, fn, title, desc in mt_cluster.PAGES:
        cbody, cld = fn(stats)
        written.append(shell.write("%s/index.html" % slug, shell.page(
            title, desc % stats, "https://mutanttools.com/%s/" % slug,
            cbody, extra_head=cld, nav_current="/maya-auto-rigger/")))

    # homepage: retitle and append the copy block below the hero
    home_path = os.path.join(SITE, "index.html")
    home = io.open(home_path, encoding="utf-8").read()
    home = mt_home.patch(home, stats, shell.DOC_CSS)
    home = shell.add_auto_rigger(home)
    io.open(home_path, "w", encoding="utf-8", newline="\n").write(home)
    written.append((home_path, len(home)))

    # llms.txt + sitemap
    for name, text in (("llms.txt", llms_txt(stats)), ("sitemap.xml", sitemap())):
        written.append(shell.write(name, text))

    # robots
    written.append(shell.write("robots.txt",
                               "User-agent: *\nAllow: /\n\n"
                               "Sitemap: https://mutanttools.com/sitemap.xml\n"))

    for path, size in written:
        print("  %-46s %7.1f KB" % (os.path.relpath(path, SITE), size / 1024.0))


if __name__ == "__main__":
    main()
