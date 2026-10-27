# -*- coding: utf-8 -*-
"""Homepage patches.

The homepage is a full-height four-panel hero and 114 words of text - the
strongest page on the domain carrying almost nothing for search to read. This
appends a content section *below* the hero and retitles the page toward the term
people actually type. The hero markup is not touched.

Patches are marker-guarded, so running the build twice replaces the section
rather than stacking another copy.
"""
import re

import mt_md as m
import mt_shell as shell

START = "<!-- mt-home-copy:start -->"
END = "<!-- mt-home-copy:end -->"

TITLE = "Maya Auto Rigger &amp; Modular Rigging Framework | Mutant Tools"
DESC = ("Mutant Tools is a free, open-source auto rigger for Autodesk Maya. %(blocks)d modular "
        "rigging blocks for biped, facial, animal, vehicle and game rigs, with a documented "
        "Python API. No licence, no seat count.")
H1 = "Mutant Tools &ndash; a free auto rigger and modular rigging framework for Autodesk Maya"

# (icon, who, why)
AUDIENCE = [
    ("build", "Riggers",
     "Stop typing the same four hundred operations on every character. Templates for the "
     "standard cases, blocks for everything else."),
    ("code", "Technical directors",
     "Every command is public Python. Batch rebuilds, asset checks and pipeline integration "
     "are ordinary scripting, not reverse engineering."),
    ("settings", "Studios",
     "Naming conventions and rig defaults are JSON config. Fork them once and every rig the "
     "team builds follows the house standard."),
]

# (href, title, text)
GUIDES = [
    ("/maya-auto-rigger/", "Maya auto rigger",
     "The whole system: how block-based rigging differs from a fixed skeleton, what it covers, "
     "requirements and FAQ."),
    ("/maya-facial-rigging/", "Facial rigging",
     "Twenty face modules &mdash; jaw, mouth, eyelids, brows, sticky lips &mdash; and the order "
     "to build them in."),
    ("/maya-animal-rigging/", "Animal rigging",
     "Quadruped limbs and spines, wings, tails, snakes, and eight creature templates."),
    ("/game-character-rigging-maya/", "Game rigging",
     "Clean exportable skeletons, joint budgets, joint-based correctives, Unreal and MetaHuman."),
    ("/free-maya-rigging-tools/", "Free rigging tools",
     "Everything in the box: the rig tools window, skinning, mocap, crowds, versioning."),
    ("/developer/", "Python API",
     "Write your own blocks. The mt object, the build lifecycle, and a complete worked example."),
]


def _band_head(kicker, title, anchor, body):
    """A band's opening row: kicker and headline on the left, prose on the right."""
    return ('<div class="mt-split"><div><p class="mt-kicker">%s</p><h2 id="%s">%s</h2></div>'
            '<div class="mt-body">%s</div></div>' % (kicker, anchor, title, body))


def _section(stats):
    b = [START, '<div class="mt-doc mt-home" id="mt-home-copy">']
    A = b.append

    A('<section class="mt-band"><div class="mt-wrap">')
    A(_band_head(
        "01 / What it is", "A Maya auto rigger built out of blocks", "what-it-is",
        "<p>Mutant Tools rigs characters, creatures, vehicles and props in Autodesk Maya. "
        "Instead of one fixed skeleton you drop into every asset, a rig is a stack of "
        "independent <b>blocks</b> &mdash; one per piece of anatomy. A spine block, two limb "
        "blocks, a head, a jaw, a tail if the character has one.</p>"
        "<p>You place guides on the mesh, set each block's options, and press build. Blocks "
        "run top to bottom in outliner order and produce the rig. Change a guide and build "
        "again: the blocks are what you keep, the rig is disposable output. That is what makes "
        "a note on day forty of animation survivable.</p>"))
    A('<ul class="mt-stats mt-stats--tiles">'
      '<li><b>%(blocks)d</b><span>rigging blocks</span></li>'
      '<li><b>19</b><span>character templates</span></li>'
      '<li><b>%(methods)d</b><span>python commands</span></li>'
      '<li><b>$0</b><span>no licence server</span></li>'
      '</ul>' % stats)
    A('</div></section>')

    A('<section class="mt-band"><div class="mt-wrap">')
    A('<p class="mt-kicker">02 / Audience</p><h2 id="who">Who it is for</h2>')
    A('<div class="mt-grid mt-grid--3">')
    for ico, who, why in AUDIENCE:
        A('<div class="mt-card"><span class="mt-card__icon">%s</span><h3>%s</h3><p>%s</p></div>'
          % (m.icon(ico), who, why))
    A('</div></div></section>')

    A('<section class="mt-band"><div class="mt-wrap">')
    A(_band_head(
        "03 / Coverage", "What it rigs", "what-it-rigs",
        "<p>Bipeds, faces, quadrupeds, birds, snakes, insects, cars, props and cloth &mdash; and "
        "combinations of those, because nothing in the system objects to a human torso on "
        "digitigrade legs with wings.</p>"))
    A('<div class="mt-grid mt-grid--3">')
    for href, title, text in GUIDES:
        A('<div class="mt-card"><h3><a href="%s">%s</a></h3><p>%s</p>'
          '<span class="mt-card__go">Read the guide %s</span></div>'
          % (href, title, text, m.icon("chevron-right")))
    A('</div></div></section>')

    A('<section class="mt-band"><div class="mt-wrap">')
    A(_band_head(
        "04 / Licence", "Free, and open", "free",
        "<p>Mutant Tools is free to download and the source is public on GitHub. There is no "
        "licence server, no node-locked key and no watermark on the rigs it produces. Use it on "
        "commercial work. If the site vanished tomorrow your copy would keep working, and you "
        "could still fix it yourself.</p>"
        "<p>Install by dragging <code>easy_install.py</code> into a Maya viewport. Maya 2022 or "
        "newer.</p>"))
    A('<div class="mt-cta mt-cta--split"><div><h2>Download Mutant Tools</h2>'
      '<p>One file into Maya and it is installed, with the shelf and the menu set up for you.</p>'
      '</div>%s</div>'
      % m.actions(m.btn("Get it on GitHub", "https://github.com/RenderDeMartes/Mutant_Tools"),
                  m.btn("How it works", "/maya-auto-rigger/", ghost=True)))
    A('</div></section>')

    A('</div>')
    A(END)
    return "\n".join(b)


def patch(html, stats):
    """Apply every homepage edit. Safe to run repeatedly."""
    out = html

    out = re.sub(r"<title>.*?</title>", "<title>%s</title>" % TITLE, out, count=1, flags=re.S)
    out = re.sub(r'<meta name="description" content="[^"]*">',
                 '<meta name="description" content="%s">' % (DESC % stats), out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*">',
                 '<meta property="og:title" content="%s">' % TITLE, out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*">',
                 '<meta property="og:description" content="%s">' % (DESC % stats), out, count=1)

    # The h1 is class="visually-hidden", so its text can change with no visual effect.
    out = re.sub(r'(<h1 class="visually-hidden">\s*).*?(\s*</h1>)',
                 lambda mo: mo.group(1) + H1 + mo.group(2), out, count=1, flags=re.S)

    # The homepage links the same stylesheet as every other page. Drop the old
    # inline copy of the previous styles if a page still carries it, and refresh
    # the link so a CSS edit's new hash lands here too.
    out = re.sub(r'<style id="mt-docs">.*?</style>\s*', "", out, count=1, flags=re.S)
    if 'id="mt-ui"' in out:
        out = re.sub(r'<link rel="stylesheet" id="mt-ui" href="[^"]*">', lambda _: shell.DOC_CSS,
                     out, count=1)
    else:
        out = out.replace("</head>", shell.DOC_CSS + "\n</head>", 1)

    section = _section(stats)
    if START in out and END in out:
        out = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: section, out, flags=re.S)
    else:
        # Sits inside .entry-content, after the hero section closes.
        marker = '</div><!-- .entry-content .clear -->'
        if marker not in out:
            raise RuntimeError("homepage: entry-content marker not found, refusing to guess")
        out = out.replace(marker, section + "\n" + marker, 1)

    return out
