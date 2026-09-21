# -*- coding: utf-8 -*-
"""Homepage patches.

The homepage is a full-height four-panel hero and 114 words of text - the
strongest page on the domain carrying almost nothing for search to read. This
appends a content section *below* the hero and retitles the page toward the term
people actually type. The hero markup is not touched, so the design is unchanged.

Patches are marker-guarded, so running the build twice replaces the section
rather than stacking another copy.
"""
import re

START = "<!-- mt-home-copy:start -->"
END = "<!-- mt-home-copy:end -->"

TITLE = "Maya Auto Rigger &amp; Modular Rigging Framework | Mutant Tools"
DESC = ("Mutant Tools is a free, open-source auto rigger for Autodesk Maya. %(blocks)d modular "
        "rigging blocks for biped, facial, animal, vehicle and game rigs, with a documented "
        "Python API. No licence, no seat count.")
H1 = "Mutant Tools &ndash; a free auto rigger and modular rigging framework for Autodesk Maya"


def _section(stats):
    return """%(start)s
<div class="mt-doc" id="mt-home-copy">
  <div class="mt-wrap mt-body" style="padding-top:5rem;padding-bottom:1rem">

    <h2 id="what-it-is">A Maya auto rigger built out of blocks</h2>
    <p>Mutant Tools rigs characters, creatures, vehicles and props in Autodesk Maya. Instead of one
    fixed skeleton you drop into every asset, a rig is a stack of independent <b>blocks</b> &mdash;
    one per piece of anatomy. A spine block, two limb blocks, a head, a jaw, a tail if the character
    has one.</p>

    <p>You place guides on the mesh, set each block's options, and press build. Blocks run top to
    bottom in outliner order and produce the rig. Change a guide and build again: the blocks are
    what you keep, the rig is disposable output. That is what makes a note on day forty of
    animation survivable.</p>

    <ul class="mt-stats" style="margin:2.5rem 0 3rem">
      <li><b>%(blocks)d</b><span>rigging blocks</span></li>
      <li><b>19</b><span>character templates</span></li>
      <li><b>%(methods)d</b><span>python commands</span></li>
      <li><b>$0</b><span>no licence server</span></li>
    </ul>

    <h2 id="who">Who it is for</h2>
    <div class="mt-grid mt-grid--3">
      <div class="mt-card"><h4>Riggers</h4><p>Stop typing the same four hundred operations on every
      character. Templates for the standard cases, blocks for everything else.</p></div>
      <div class="mt-card"><h4>Technical directors</h4><p>Every command is public Python. Batch
      rebuilds, asset checks and pipeline integration are ordinary scripting, not reverse
      engineering.</p></div>
      <div class="mt-card"><h4>Studios</h4><p>Naming conventions and rig defaults are JSON config.
      Fork them once and every rig the team builds follows the house standard.</p></div>
    </div>

    <h2 id="what-it-rigs">What it rigs</h2>
    <p>Bipeds, faces, quadrupeds, birds, snakes, insects, cars, props and cloth &mdash; and
    combinations of those, because nothing in the system objects to a human torso on digitigrade
    legs with wings.</p>

    <div class="mt-grid mt-grid--2">
      <div class="mt-card"><h4><a href="/maya-auto-rigger/">Maya auto rigger</a></h4>
      <p>The whole system: how block-based rigging differs from a fixed skeleton, what it covers,
      requirements and FAQ.</p></div>
      <div class="mt-card"><h4><a href="/maya-facial-rigging/">Facial rigging</a></h4>
      <p>Twenty face modules &mdash; jaw, mouth, eyelids, brows, sticky lips &mdash; and the order
      to build them in.</p></div>
      <div class="mt-card"><h4><a href="/maya-animal-rigging/">Animal rigging</a></h4>
      <p>Quadruped limbs and spines, wings, tails, snakes, and eight creature templates.</p></div>
      <div class="mt-card"><h4><a href="/game-character-rigging-maya/">Game rigging</a></h4>
      <p>Clean exportable skeletons, joint budgets, joint-based correctives, Unreal and
      MetaHuman.</p></div>
      <div class="mt-card"><h4><a href="/free-maya-rigging-tools/">Free rigging tools</a></h4>
      <p>Everything in the box: the rig tools window, skinning, mocap, crowds, versioning.</p></div>
      <div class="mt-card"><h4><a href="/developer/">Python API</a></h4>
      <p>Write your own blocks. The mt object, the build lifecycle, and a complete worked
      example.</p></div>
    </div>

    <h2 id="free">Free, and open</h2>
    <p>Mutant Tools is free to download and the source is public on GitHub. There is no licence
    server, no node-locked key and no watermark on the rigs it produces. Use it on commercial work.
    If the site vanished tomorrow your copy would keep working, and you could still fix it
    yourself.</p>

    <p>Install by dragging <code>easy_install.py</code> into a Maya viewport. Maya 2022 or newer.</p>

    <div class="mt-cta" style="margin-bottom:4rem">
      <h2>Download Mutant Tools</h2>
      <p>One file into Maya and it is installed, with the shelf and the menu set up for you.</p>
      <a class="mt-btn" href="https://github.com/RenderDeMartes/Mutant_Tools" target="_blank"
         rel="noopener">Get it on GitHub</a>
      <a class="mt-btn mt-btn--ghost" href="/maya-auto-rigger/">How it works</a>
    </div>

  </div>
</div>
%(end)s""" % dict(start=START, end=END, **stats)


def patch(html, stats, doc_css):
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

    # The docs stylesheet. Replace any previous copy rather than skipping when
    # one exists, or a later CSS change would never reach the homepage.
    if 'id="mt-docs"' in out:
        out = re.sub(r'<style id="mt-docs">.*?</style>', lambda _: doc_css.strip(),
                     out, count=1, flags=re.S)
    else:
        out = out.replace("</head>", doc_css + "\n</head>", 1)

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
