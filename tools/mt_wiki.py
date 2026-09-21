# -*- coding: utf-8 -*-
"""Builds /wiki/ - the Mutant Tools command and block reference.

The old wiki was sphinx-apidoc output: one stub page per module, no signatures
worth reading and no way to search it. This one is generated straight from the
AST of tools/kinematics/modules/main_mutant and from every block launcher JSON,
so it cannot drift from the code. Filtering is client side over the rendered
DOM, so it works with no build step and no search index to keep in sync.
"""
import mt_md as m

CAT_LABELS = {
    "000_Presets": "Presets",
    "001_Studio": "Studio fixes",
    "002_Biped": "Biped",
    "003_Facial": "Facial",
    "004_Animals": "Animals",
    "005_Clothes": "Clothes",
    "006_Vehicles": "Vehicles",
    "007_Games": "Games",
    "008_Props": "Props",
    "009_Data": "Data",
    "010_Other": "Other",
}

CAT_BLURB = {
    "000_Presets": "Whole-character templates. One click drops a full block stack in the outliner, "
                   "ready for guide placement.",
    "001_Studio": "Post-build fixes and conventions a studio wants applied to every asset.",
    "002_Biped": "Human body modules - spine, limbs, hands, feet, head.",
    "003_Facial": "Face modules, from jaw and mouth down to sticky lips and pupil dilation.",
    "004_Animals": "Quadrupeds, wings, tails and other non-biped anatomy.",
    "005_Clothes": "Secondary cloth and accessory rigs.",
    "006_Vehicles": "Cars and machinery - wheels, doors, steering, drift.",
    "007_Games": "Game-engine oriented blocks and body conversion.",
    "008_Props": "General purpose building blocks. The ones to read first when writing your own.",
    "009_Data": "Blocks that reapply saved data - skin weights, control shapes - as part of the build.",
    "010_Other": "Utility blocks, including the base rig and the code/stop blocks.",
}

SEARCH_JS = """
<script>
(function(){
  var box = document.getElementById('mt-q');
  if(!box) return;
  var items = [].slice.call(document.querySelectorAll('[data-search]'));
  var groups = [].slice.call(document.querySelectorAll('[data-group]'));
  var count = document.getElementById('mt-count');
  var pills = [].slice.call(document.querySelectorAll('.mt-pill'));
  var total = items.length;
  var filter = '';

  function apply(){
    var q = box.value.trim().toLowerCase();
    var shown = 0;
    items.forEach(function(el){
      var hay = el.getAttribute('data-search');
      var grp = el.getAttribute('data-cat') || '';
      var okQ = !q || hay.indexOf(q) !== -1;
      var okF = !filter || grp === filter;
      var on = okQ && okF;
      el.classList.toggle('mt-hide', !on);
      if(on) shown++;
    });
    groups.forEach(function(g){
      var any = g.querySelector('[data-search]:not(.mt-hide)');
      g.classList.toggle('mt-hide', !any);
    });
    if(count) count.textContent = (q || filter)
      ? shown + ' of ' + total + ' shown'
      : total + ' entries';
  }

  box.addEventListener('input', apply);
  pills.forEach(function(p){
    p.addEventListener('click', function(){
      var v = p.getAttribute('data-filter') || '';
      filter = (filter === v) ? '' : v;
      pills.forEach(function(o){
        o.setAttribute('aria-pressed', String(o.getAttribute('data-filter') === filter && filter !== ''));
      });
      apply();
    });
  });
  apply();
})();
</script>
"""

SEARCH_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
               '<path d="M20 20l-4-4"/></svg>')


def _docstring_rest(full, summary):
    """Everything after the one-line summary, kept in the author's own formatting.

    Several docstrings end with a few paragraphs restating the implementation
    line by line. Those are dropped: the signature and the Args block carry the
    same information, and the source is one click away.
    """
    if not full:
        return ""
    body = full
    if summary and body.startswith(summary):
        body = body[len(summary):]
    kept = []
    for para in body.split("\n\n"):
        stripped = para.strip()
        if not stripped:
            continue
        # narrative restatements of the code - long, prose, no section header
        if (stripped.startswith(("This function", "The function", "It then", "Note:"))
                and ":" not in stripped.split("\n")[0][:30]
                and len(stripped) > 160):
            continue
        kept.append(para.rstrip())
    return "\n\n".join(kept).strip()


def _searchbox(placeholder):
    return ('<div class="mt-search">%s<input id="mt-q" type="search" autocomplete="off" '
            'spellcheck="false" placeholder="%s" aria-label="%s"></div>\n'
            % (SEARCH_ICON, placeholder, placeholder))


# --------------------------------------------------------------------- index
def index(stats):
    b = []
    A = b.append
    A('<header class="mt-hero"><div class="mt-wrap">')
    A('<p class="mt-kicker">Wiki</p>')
    A('<h1>Mutant Tools reference</h1>')
    A('<p class="mt-lede">Every <code>mt</code> command and every shipped block, generated from '
      'the source at each release. Searchable, and accurate by construction.</p>')
    A('<ul class="mt-stats">'
      '<li><b>%d</b><span>commands</span></li>'
      '<li><b>%d</b><span>blocks</span></li>'
      '<li><b>%d</b><span>categories</span></li>'
      '<li><b>%d</b><span>control shapes</span></li></ul>' %
      (stats["methods"], stats["blocks"], stats["categories"], stats["curves"]))
    A('</div></header>')

    A('<div class="mt-wrap"><div class="mt-body" style="margin-top:3rem">')
    A(m.cards([
        ("Commands", 'All %d <code>mt</code> methods with full signatures, grouped by the class '
         'they come from. <a href="/wiki/commands/">Browse commands</a>' % stats["methods"]),
        ("Blocks", 'All %d blocks with their options, icons and build commands. '
         '<a href="/wiki/blocks/">Browse blocks</a>' % stats["blocks"]),
        ("Developer guide", 'How the block system fits together, and how to write your own. '
         '<a href="/developer/">Read the guide</a>'),
    ], 3))

    A(m.h2("Start here", "start"))
    A(m.code("""
        from maya import cmds
        from Mutant_Tools.Utils.Rigging import main_mutant

        mt = main_mutant.Mutant()
        nc, curve_data, setup = mt.import_configs()
        """, "every session"))
    A("<p>Those two lines precede everything else on this site. <code>mt</code> is the whole API; "
      "<code>nc</code>, <code>curve_data</code> and <code>setup</code> are the JSON configs that "
      "keep naming and defaults out of your rigging code.</p>")

    A(m.h2("Where things live", "layout"))
    A(m.table(["Path", "What"], [
        ["<code>Utils/Rigging/tools.py</code>", "Controls, attributes, colour, nodes, JSON, matrices"],
        ["<code>Utils/Rigging/kinematics.py</code>", "FK, IK, twist, ribbons, spines, deformers"],
        ["<code>Utils/Rigging/modules.py</code>", "Blocks, guides, base rig hierarchy, dev mode"],
        ["<code>Utils/Rigging/main_mutant.py</code>", "The <code>Mutant</code> class and updates"],
        ["<code>Blocks/&lt;category&gt;/&lt;block&gt;/</code>", "One folder per block: launcher JSON, versioned JSON, exec script"],
        ["<code>config/name_conventions.json</code>", "<code>nc</code> - every suffix and side token"],
        ["<code>config/rig_setup.json</code>", "<code>setup</code> - default shapes, colours, axes, groups"],
        ["<code>config/curves.json</code>", "<code>curve_data</code> - the control shape library"],
        ["<code>UI/</code>", "AutoRigger, BlockBuilder, RigTools, Helpers and the rest of the windows"],
        ["<code>Docs/AI_MT_COMMAND_RULES.md</code>", "Coding rules written for AI assistants"],
    ]))

    A(m.h2("The older Sphinx wiki", "sphinx"))
    A('<p>The previous autodoc build is still online at '
      '<a href="/docs/_build/html/index.html">/docs/_build/html/</a>. It covers the same modules '
      'in less depth and is no longer regenerated - keep it bookmarked only if you have old links '
      'pointing into it.</p>')

    A('<div class="mt-cta"><h2>Writing a block?</h2>'
      '<p>The developer guide walks the whole lifecycle, from the launcher JSON through the build '
      'loop to shipping a v002 without breaking last year\'s scenes.</p>'
      '<a class="mt-btn" href="/developer/">Developer guide</a>'
      '<a class="mt-btn mt-btn--ghost" href="/wiki/commands/">Command reference</a></div>')
    A('</div></div>')
    return "".join(b)


# ------------------------------------------------------------------ commands
CLASS_BLURB = [
    ("Tools_class", "tools.py", "Controls, attributes, colour, utility nodes, JSON and geometry queries."),
    ("Kinematics_class", "kinematics.py", "FK and IK systems, twist, ribbons, spines, deformers, LODs."),
    ("Modules_class", "modules.py", "Blocks, guides, joint orientation and the base rig hierarchy."),
    ("Mutant", "main_mutant.py", "Version checks and in-place updates from GitHub."),
]


def commands(api):
    b = []
    A = b.append
    total = sum(len([x for x in api[c]["methods"] if not x[0].startswith("_")])
                for c, _, _ in [(a, b_, c_) for a, b_, c_ in CLASS_BLURB])

    A('<header class="mt-hero"><div class="mt-wrap">')
    A('<p class="mt-kicker"><a href="/wiki/" style="color:inherit">Wiki</a> / Commands</p>')
    A('<h1>Command reference</h1>')
    A('<p class="mt-lede">Every public method on <code>mt</code>, with its real signature and '
      'defaults, read from the source. Click any row to expand.</p>')
    A('</div></header>')

    A('<div class="mt-wrap"><div class="mt-body" style="margin-top:3rem">')
    A(_searchbox("Search commands - try curve, twist, attr, mirror"))
    A('<ul class="mt-pills">')
    for cls, fname, _ in CLASS_BLURB:
        A('<button class="mt-pill" type="button" data-filter="%s" aria-pressed="false">%s</button>'
          % (cls, fname))
    A('</ul>')
    A('<p class="mt-count" id="mt-count">%d entries</p>' % total)

    for cls, fname, blurb in CLASS_BLURB:
        meths = [x for x in api[cls]["methods"] if not x[0].startswith("_")]
        if not meths:
            continue
        A('<section data-group>')
        A(m.h2("%s <span style=\"font-size:.55em;color:var(--mt-dim);font-weight:400\">%s</span>"
               % (cls.replace("_class", ""), fname), m.slug(cls)))
        A("<p>%s</p>" % blurb)
        for entry in sorted(meths, key=lambda x: x[0]):
            name, sig, summary, lineno = entry[0], entry[1], entry[2], entry[3]
            full = entry[4] if len(entry) > 4 else summary
            hay = (name + " " + sig + " " + full).lower()
            pretty_sig = m.esc(sig)
            A('<details class="mt-api" data-search="%s" data-cat="%s">' % (m.esc(hay), cls))
            A('<summary><span class="mt-sig">mt.<b>%s</b>(%s)</span>'
              '<span class="mt-from">%s:%d</span></summary>' % (name, pretty_sig, fname, lineno))
            A('<div class="mt-api-body">')
            A("<p>%s</p>" % (m.esc(summary) if summary else
                             "<i style='color:var(--mt-dim)'>No docstring in the source.</i>"))
            A(m.code("mt.%s(%s)" % (name, sig), "signature"))
            rest = _docstring_rest(full, summary)
            if rest:
                A('<pre class="mt-docstring"><code>%s</code></pre>' % m.esc(rest))
            A('</div></details>')
        A('</section>')

    A('</div></div>')
    A(SEARCH_JS)
    return "".join(b)


# -------------------------------------------------------------------- blocks
TYPE_WORD = {"string": "string", "enum": "enum", "float": "int 1-20", "bool": "bool"}


def _attr_rows(attrs):
    rows = []
    for key in sorted(attrs.keys()):
        value = attrs[key]
        kind = ""
        for word in ("string", "enum", "float", "bool"):
            if word in key:
                kind = TYPE_WORD[word]
                break
        nice = key.rsplit("_", 1)[0]
        if kind == "enum":
            shown = " &middot; ".join("<code>%s</code>" % m.esc(v) for v in str(value).split(":")[:8])
            if len(str(value).split(":")) > 8:
                shown += " &hellip;"
        else:
            shown = "<code>%s</code>" % m.esc(str(value)) if str(value) else "<i>empty</i>"
        rows.append(["<code>%s</code>" % m.esc(nice), kind, shown])
    return rows


def blocks(cats):
    b = []
    A = b.append
    total = sum(len(v) for v in cats.values())

    A('<header class="mt-hero"><div class="mt-wrap">')
    A('<p class="mt-kicker"><a href="/wiki/" style="color:inherit">Wiki</a> / Blocks</p>')
    A('<h1>Block catalogue</h1>')
    A('<p class="mt-lede">All %d blocks that ship with Mutant Tools, with the options each one '
      'exposes on its config node and the exact command the builder calls.</p>' % total)
    A('</div></header>')

    A('<div class="mt-wrap"><div class="mt-body" style="margin-top:3rem">')
    A(_searchbox("Search blocks - try spine, eyelid, wheel, skin"))
    A('<ul class="mt-pills">')
    for cat in cats:
        A('<button class="mt-pill" type="button" data-filter="%s" aria-pressed="false">%s</button>'
          % (cat, CAT_LABELS.get(cat, cat)))
    A('</ul>')
    A('<p class="mt-count" id="mt-count">%d entries</p>' % total)

    for cat, items in cats.items():
        A('<section data-group>')
        A(m.h2("%s <span style=\"font-size:.55em;color:var(--mt-dim);font-weight:400\">%s</span>"
               % (CAT_LABELS.get(cat, cat), cat), m.slug(cat)))
        if cat in CAT_BLURB:
            A("<p>%s</p>" % CAT_BLURB[cat])
        for it in items:
            hay = " ".join([it["folder"], it["name"], it["desc"],
                            " ".join(it["attrs"].keys())]).lower()
            A('<details class="mt-api" data-search="%s" data-cat="%s">' % (m.esc(hay), cat))
            # Several presets share a JSON "Name", so the folder is the stable
            # label - and it is also what the AutoRigger tree shows.
            label = m.re.sub(r"^\d+_", "", it["folder"]).replace("_", " ")
            A('<summary><span class="mt-sig"><b>%s</b></span>'
              '<span style="color:var(--mt-dim);font-size:.85rem">%s</span>'
              '<span class="mt-from">%s</span></summary>'
              % (m.esc(label), m.esc(it["desc"][:88]), m.esc(it["folder"])))
            A('<div class="mt-api-body">')
            if it["desc"]:
                A("<p>%s</p>" % m.esc(it["desc"]))
            meta = []
            if it["name"]:
                meta.append("Default block name <code>%s</code>" % m.esc(it["name"]))
            if it["icon"]:
                meta.append("icon <code>%s</code>" % m.esc(it["icon"]))
            if it["pyfile"]:
                meta.append("<code>%s</code>" % m.esc(it["pyfile"]))
            if meta:
                A('<p style="font-size:.82rem;color:var(--mt-dim)">%s</p>' % " &middot; ".join(meta))
            A(m.code("%s\n%s" % (it["create"] or "", it["build"] or ""), "commands"))
            rows = _attr_rows(it["attrs"])
            if rows:
                A("<h4>Config attributes</h4>")
                A(m.table(["Attribute", "Type", "Default / options"], rows))
            if it["help"]:
                A("<h4>Artist help text</h4>")
                A(m.plain(it["help"].replace("\\n", "\n"), "Help"))
            A('</div></details>')
        A('</section>')

    A('<div class="mt-cta"><h2>Write your own</h2>'
      '<p>A block is a folder with a JSON and a Python file. Drop it into '
      '<code>Blocks/</code> and the AutoRigger finds it - no registration step.</p>'
      '<a class="mt-btn" href="/developer/#first-block">Write your first block</a></div>')
    A('</div></div>')
    A(SEARCH_JS)
    return "".join(b)
