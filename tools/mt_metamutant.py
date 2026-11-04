# -*- coding: utf-8 -*-
"""/meta-mutant/: the Meta Mutant tutorial, for people who are not riggers.

Help > Tutorial in Maya's Meta Mutant window opens this page. Short on purpose: what
an animator needs comes first, and AI is an optional helper, never a requirement.
The pictures and videos are in assets/img/meta-mutant/, the widgets in
assets/js/meta-mutant.js.
"""
import hashlib, io, os

import mt_md as m
import mt_shell as shell

IMG = "/assets/img/meta-mutant/"
JS_PATH = os.path.join(shell.SITE, "assets", "js", "meta-mutant.js")

TITLE = "Meta Mutant Tutorial - MetaHuman Face Rig on a Custom Head | Mutant Tools"
DESC = ("Move the MetaHuman face rig onto a custom head in Maya, in four steps. The result is "
        "vanilla Maya 2026: animators need no custom nodes, plugin or Mutant Tools.")
GUIDE = "https://raw.githubusercontent.com/RenderDeMartes/Mutant_Tools/main/Docs/AI_META_MUTANT.md"
# Every prompt starts here: it must work on a computer where Claude Code knows nothing of Mutant Tools.
START = ("Find Mutant Tools on this computer: the Mutant_Tools folder in Maya's scripts folder, usually "
         "Documents/maya/2026/scripts. Read Docs/AI_META_MUTANT.md inside it, or " + GUIDE + " if it is not "
         "there, and follow it to connect to my open Maya. Ask me before saving anything. Then: ")
HEAD_SITE = 'Jean Leal (<a href="https://jeanleart3d.com/" target="_blank" rel="noopener">jeanleart3d.com</a>)'


def _js_src():
    digest = hashlib.sha1(io.open(JS_PATH, "rb").read()).hexdigest()[:10]
    return "/assets/js/meta-mutant.js?v=%s" % digest


def _img(name, alt, extra=""):
    return '<img src="%s%s.webp" alt="%s" loading="lazy"%s>' % (IMG, name, alt, extra)


def _ai(prompt, text=""):
    """A step's optional Claude note, closed until someone wants it."""
    body = "<p>%s</p>" % text if text else ""
    return ('<details class="mm-ai"><summary>Optional: with Claude</summary>%s%s</details>'
            % (body, _prompt(prompt)))


def _prompt(text):
    """A complete prompt, with the part that finds the tool, shown whole."""
    return '<div class="mm-prompt" data-copy><code>%s%s</code></div>' % (START, text)


def _task(text):
    """A prompt shown as its task alone. Copying it adds the start, shown once above the list."""
    return '<div class="mm-prompt" data-copy data-start="%s"><code>%s</code></div>' % (START, text)


def _band(number, label, title, section_id=""):
    ident = ' id="%s"' % section_id if section_id else ""
    return ('<section class="mt-band"%s><div class="mt-wrap"><p class="mt-kicker">%s / %s</p><h2>%s</h2>'
            % (ident, number, label, title))


END = "</div></section>"


def _step(number, where, title, body, media=""):
    return ('<article class="mm-step" id="step-%s"><div class="mm-step__text"><p class="mt-kicker">%s / %s</p>'
            '<h3>%s</h3>%s</div>%s</article>' % (number, number, where, title, body,
                                                 '<div class="mm-step__media">%s</div>' % media if media else ""))


def _compare(after, before, alt_after, alt_before, label_before="Before", label_after="After"):
    return ('<div class="mm-cmp" data-cmp>%s<div class="mm-cmp__top">%s</div><div class="mm-cmp__knob"></div>'
            '<span class="mm-cmp__label mm-cmp__label--a">%s</span><span class="mm-cmp__label mm-cmp__label--b">%s</span>'
            '<input type="range" min="0" max="100" value="50" aria-label="Compare %s and %s"></div>'
            % (_img(after, alt_after), _img(before, alt_before), label_before, label_after, label_before, label_after))


def _eye(cy, pivot_class, colour, caption, alt):
    return ('<figure class="mm-eye"><svg viewBox="0 0 200 180" role="img" aria-label="%s">'
            '<circle class="mm-eye__socket" cx="100" cy="90" r="62"/>'
            '<g class="mm-eye__ball %s"><circle class="mm-eye__white" cx="100" cy="90" r="50"/>'
            '<circle class="mm-eye__iris" cx="100" cy="46" r="16"/><circle class="mm-eye__pupil" cx="100" cy="42" r="7"/></g>'
            '<circle cx="100" cy="%d" r="6" fill="%s"/></svg><figcaption>%s</figcaption></figure>'
            % (alt, pivot_class, cy, colour, caption))


CHANGES = [
    ("Lips crossed with the jaw open (lowest gap)", "-1.28", "1.18", "Artist"),
    ("Mouth corners stuck when opening", "Stuck", "Tapered", "Artist"),
    ("Eye center slid while looking around", "1.27", "0.00", "Artist"),
    ("Jaw hinge split in two (distance apart)", "2.7", "0", "Claude check"),
    ("Upper teeth pulled by the jaw (worst tooth)", "75%", "0%", "Artist"),
    ("Lids overlapped at full blink (MetaHuman: 0.20)", "1.08", "0.41", "Claude check"),
    ("Lower teeth through the skin", "32 of 103 poses", "Moved back 1.16, same size", "Artist"),
    ("Original meshes visible inside the rig", "Visible", "Hidden on Apply", "Artist"),
    ("Green eyes and teeth (no shader on the materials)", "Green", "Plain lambert", "Artist"),
    ("Pick Points crashed with a rig in the scene", "Crash", "Opens", "Claude check"),
    ("Face board framed too small", "Tiny", "Fills the view", "Claude check"),
]


def build(stats):
    b = []
    A = b.append
    A('<header class="mt-hero"><div class="mt-wrap mm-hero"><div>'
      '<p class="mt-kicker"><a href="/maya-facial-rigging/">Facial rigging</a> / Tutorial</p>'
      '<h1>Meta Mutant</h1>'
      '<p class="mt-lede">Moves Epic&rsquo;s MetaHuman face rig onto a custom head in Maya, in four steps.</p>')
    A(m.ok("<p><b>Vanilla Maya 2026.</b> No custom nodes, no plugin to install, no Mutant Tools needed. "
           "Send the Maya scene file: there is nothing else to bring.</p>", "For animators"))
    A('</div><video src="%shero.mp4" poster="%shero_poster.webp" autoplay muted loop playsinline '
      'aria-label="The rigged head playing five expressions"></video></div></header>' % (IMG, IMG))

    # ------------------------------------------------------------ dependencies
    A(_band("01", "Dependencies", "What you need", "dependencies"))
    A('<div class="mt-grid mt-grid--2"><div class="mt-card"><p>%s</p><h3>To animate with it</h3><ul class="mm-list">'
      '<li><b>Maya 2026.</b> Older versions are not supported: the rig uses a node type Maya 2024 cannot load.</li>'
      '<li><b>The scene file.</b> No references or external files. This test scene is 428 MB.</li>'
      '<li><b>Built from</b> standard joints, skinCluster, blendShape and math nodes.</li></ul></div>'
      '<div class="mt-card"><p>%s</p><h3>To build a new rig</h3><ul class="mm-list">'
      '<li>Maya 2026</li><li>Mutant Tools, which includes Meta Mutant and TopoTransfer</li>'
      '<li>A MetaHuman DNA file, from Epic&rsquo;s download</li><li>A web browser, for the fitting step</li>'
      '<li>A head model, facing forward with its mouth closed</li></ul></div></div>'
      % (m.chip("Animators"), m.chip("Riggers", "deep")))
    A('<p class="mt-meta">Tested by opening the scene in a clean Maya 2026 session without Mutant Tools: the '
      'animation and controls drove the head, eyes and teeth. The scene also lists lookdevKit, Arnold (mtoa) and '
      'stereoCamera, which come with a standard Maya install. The rig&rsquo;s motion does not use them. AI is not '
      'required at any step.</p>')
    A(END)

    # ------------------------------------------------------------------ content
    A(_band("02", "The rig", "What it contains", "rig"))
    A('<ul class="mt-stats mt-stats--tiles mm-stats"><li><b>870</b><span>Joints, for large moves</span></li>'
      '<li><b>737</b><span>Face shapes, for detail</span></li><li><b>174</b><span>Animator controls</span></li>'
      '<li><b>39</b><span>Sounds posed in the tests</span></li></ul>')
    A('<div class="mt-grid mt-grid--2 mm-pair"><figure class="mm-shot">%s</figure><figure class="mm-shot">%s</figure></div>'
      % (_img("skeleton", "The head with its facial joints drawn over it"),
         _img("board", "The face board: a drawing of a face covered in sliders")))
    A('<div class="mt-split mm-model"><div><h3>The model</h3><p class="mt-meta">Head by %s. The wires are its '
      'topology. The loops around the eyes and mouth are where the skin folds.</p></div>'
      '<div class="mm-topo"><figure class="mm-shot">%s</figure><div><figure class="mm-shot">%s</figure>'
      '<figure class="mm-shot">%s</figure></div></div></div>'
      % (HEAD_SITE, _img("topo_face", "Front view of the head with its wireframe topology"),
         _img("topo_34", "Three quarter view of the wireframe"), _img("topo_mouth", "The wires around the mouth")))
    A(END)

    # ----------------------------------------------------------------- workflow
    A(_band("03", "Workflow", "Four steps", "workflow"))
    A(_step("01", "Maya, artist", "Pick points",
            "<p>Mark the same places on your head as on the MetaHuman, which is already marked: 30 points, "
            "the lips, the eyelids, then the eye and teeth meshes.</p>"
            + _ai("Open Meta Mutant for the head mesh I have selected. Check its scale is 1, and ask me before freezing anything."),
            '<figure class="mm-shot">%s</figure>' % _img("ui_pick_lines", "Pick Points window: MetaHuman on the left already marked, the head on the right with its lines picked")))
    A(_step("02", "Maya, one click", "Prepare",
            "<p>Saves both heads and the picks, then opens the fitting tool in the browser with everything loaded.</p>",
            '<figure class="mm-shot mm-shot--ui">%s</figure>' % _img("ui_mm_steps", "The Meta Mutant window with four steps")))
    A(_step("03", "Browser", "TopoTransfer",
            "<p>Press <b>Fit</b>, then <b>Keep result</b> and <b>Send to Maya</b>. The MetaHuman surface takes the "
            "shape of your head. About 9 seconds on this head.</p>"
            '<p class="mt-meta">Teal is your head, grey is the MetaHuman. A mottled mix means the two surfaces match closely.</p>'
            + '<p><a class="mt-btn mt-btn--ghost mt-btn--sm" href="/topotransfer/">Learn more about TopoTransfer</a></p>'
            + _ai("TopoTransfer is open in my browser with Claude on in its Guides step. Place the guides on my head, then show me a front picture so I can check them.", "Turn on the Claude switch in TopoTransfer&rsquo;s Guides panel first."),
            _compare("tt_kept_view", "tt_loaded_view", "After the fit: surfaces match", "Before the fit: shapes differ")
            + '<figure class="mm-shot">%s<figcaption>MetaHuman topology (33,845 points) in the shape of the head by %s (4,279 points).</figcaption></figure>'
            % (_img("tt_noref_view", "MetaHuman topology in the shape of the custom head"), HEAD_SITE)))
    A(_step("04", "Maya, one click", "Apply to my head",
            "<p>Creates <code>Head_MH</code>, a rigged copy of your head, and the face board. Takes 69 to 85 seconds "
            "on this head. Your original meshes are hidden, not changed.</p>"
            "<p><b>Face + board view</b> shows the face and the controls side by side.</p>"
            + _ai("Run Apply for the head in my open Meta Mutant window. Warn me first if it would replace a rig with animation. Then render jaw open, blink and smile from the front and the side, and tell me what looks wrong."),
            '<figure class="mm-shot mm-shot--ui">%s</figure>' % _img("ui_mm_ready", "All four steps complete")))
    A(END)

    # ----------------------------------------------------------------- controls
    A('<section class="mt-band" id="controls"><div class="mt-wrap mm-board"><img id="mm-face" src="%ss_jaw_0.webp" '
      'alt="The rigged head, responding to the sliders" width="560" height="560"><div><p class="mt-kicker">04 / Controls</p>'
      '<h2>Try the controls</h2><p class="mt-meta">Drag a slider. These are frames rendered from the rig.</p>'
      '<div class="mm-sliders" id="mm-sliders"></div></div></div></section>' % IMG)

    # -------------------------------------------------------------------- poses
    A(_band("05", "Poses", "Expressions", "poses"))
    A('<div class="mm-poses"><ul class="mt-pills" id="mm-exp"></ul><img id="mm-stage" src="%sex_happy.webp" '
      'alt="The rigged head with a happy expression" width="560" height="560"></div>' % IMG)
    A(END)

    # ----------------------------------------------------------------------- ai
    A(_band("06", "Optional", "AI help", "ai"))
    A('<p class="mm-short">The whole workflow works without AI. Claude Code can help as a tool: it needs no copy of the '
      'code open, since each prompt tells it where to look. An artist still judges the result.</p>'
      '<p class="mt-kicker">Every prompt starts with</p><div class="mm-prompt mm-prompt--start"><code>%s</code></div>'
      '<p class="mt-kicker mm-then">Then ask. Copy adds the start</p><div class="mt-grid mt-grid--2 mm-prompts">' % START)
    for label, text in (
            ("Check a pose", "Jaw open looks bad on my head. Compare it with the MetaHuman, and show me close-ups from several angles."),
            ("Fix a problem", "The eyes do not rotate from the center of each eye, mostly CTRL_R_eye. Find out why, then tell me which file you would change before editing it."),
            ("Make a test animation", "Key happy, sad, angry, kissing, yelling and all the phonemes on the face board, with each pose&rsquo;s name in text at the top of the view."),
            ("Check before sharing", "Can this rig go to an animator as it is? List any custom nodes, plugins or outside files it needs.")):
        A('<div><p class="mt-kicker">%s</p>%s</div>' % (label, _task(text)))
    A('</div>' + END)

    # ------------------------------------------------------------------ changes
    A(_band("07", "Testing", "Changes made during testing", "changes"))
    A('<p class="mm-short">Found on this head and fixed in the tool, with Claude&rsquo;s help. Numbers are scene units, on a '
      'head about 62 units tall.</p>')
    A(m.table(["Issue", "Before", "Now", "Raised by"], [list(row) for row in CHANGES]))
    A('<div class="mt-grid mt-grid--2 mm-pair"><figure><div class="mm-eyes">%s%s</div><figcaption class="mt-meta">Eye pivot, as a diagram.</figcaption></figure>'
      '<figure>%s<figcaption class="mt-meta">Teeth. &ldquo;Before&rdquo; shows the original teeth visible again, as they were.</figcaption></figure></div>'
      % (_eye(62, "mm-eye__ball--off", "var(--mt-error)", "Before: off-center pivot", "Diagram: eye turning around a point in front of its center"),
         _eye(90, "mm-eye__ball--on", "var(--mt-ok)", "Now: pivot at the center", "Diagram: eye turning around its center"),
         _compare("teeth_after2", "teeth_before2", "Now: teeth inside the mouth", "Before: teeth through the skin", "Before", "Now")))
    A(END)

    # -------------------------------------------------------------------- tests
    A(_band("08", "Tests", "Animation tests", "tests"))
    A('<p class="mm-short">Full head, no audio. Epic&rsquo;s download used here has no test clip, so these are posed from the '
      'rig&rsquo;s own controls.</p><div class="mt-grid mt-grid--2 mm-pair">'
      '<figure><video src="%stest_talk.mp4" poster="%stest_talk_poster.webp" controls loop muted playsinline preload="metadata" '
      'aria-label="Talking test"></video><figcaption class="mt-meta">Talking: &ldquo;Hello, I am Meta Mutant. This is my new face.&rdquo;</figcaption></figure>'
      '<figure><video src="%stest_rom.mp4" poster="%stest_rom_poster.webp" controls loop muted playsinline preload="metadata" '
      'aria-label="Range of motion test"></video><figcaption class="mt-meta">Range of motion: 24 moves at full strength.</figcaption></figure></div>'
      % (IMG, IMG, IMG, IMG))
    A('<p class="mt-meta mt-credit">Head: %s. Face rig, DNA and board: Epic Games MetaHuman. Pictures use a temporary clay '
      'material on the head.</p>' % HEAD_SITE)
    A(END)
    A('<script src="%s" defer></script>\n' % _js_src())
    return "".join(b)
