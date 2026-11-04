# -*- coding: utf-8 -*-
"""/topotransfer/: the TopoTransfer tutorial, for people who are not riggers.

Same parts as /meta-mutant/, which links here: short, what you need first, AI as an
optional helper. The pictures are in assets/img/topotransfer/.
"""
import mt_md as m
import mt_metamutant as mm

IMG = "/assets/img/topotransfer/"

TITLE = "TopoTransfer Tutorial - Fit One Mesh onto Another, Keep Its Topology | Mutant Tools"
DESC = ("TopoTransfer fits one mesh onto the shape of another in your browser, keeping its vertex order, "
        "faces and UVs. Opens from Maya with Mutant Tools. Your meshes never leave your computer.")


def _shot(name, alt, caption=""):
    cap = "<figcaption>%s</figcaption>" % caption if caption else ""
    return '<figure class="mm-shot"><img src="%s%s.webp" alt="%s" loading="lazy">%s</figure>' % (IMG, name, alt, cap)


def _compare(after, before, alt_after, alt_before, a="Before", b="After"):
    return ('<div class="mm-cmp" data-cmp><img src="%s%s.webp" alt="%s" loading="lazy"><div class="mm-cmp__top">'
            '<img src="%s%s.webp" alt="%s" loading="lazy"></div><div class="mm-cmp__knob"></div>'
            '<span class="mm-cmp__label mm-cmp__label--a">%s</span><span class="mm-cmp__label mm-cmp__label--b">%s</span>'
            '<input type="range" min="0" max="100" value="50" aria-label="Compare %s and %s"></div>'
            % (IMG, after, alt_after, IMG, before, alt_before, a, b, a, b))


def build(stats):
    b = []
    A = b.append
    A('<header class="mt-hero"><div class="mt-wrap mm-hero"><div>'
      '<p class="mt-kicker"><a href="/meta-mutant/">Meta Mutant</a> / Tutorial</p><h1>TopoTransfer</h1>'
      '<p class="mt-lede">Fits one mesh onto the shape of another, and keeps its topology: same points, same order, same faces.</p>')
    A(m.ok("<p><b>Your meshes never leave your computer.</b> It runs in your browser, with no upload and no account.</p>", "Private"))
    A('</div>%s</div></header>' % _compare("kept", "meshes", "After: the base mesh fitted onto the head", "Before: two meshes apart"))

    A(mm._band("01", "Dependencies", "What you need", "dependencies"))
    A('<div class="mt-grid mt-grid--2"><div class="mt-card"><h3>To use it</h3><ul class="mm-list"><li>Maya with Mutant Tools, to open it and receive the result</li>'
      '<li>A desktop browser with WebGL 2: Chrome, Edge or Firefox</li><li>Two meshes, or OBJ, PLY or STL files</li></ul></div>'
      '<div class="mt-card"><h3>Two meshes</h3><ul class="mm-list"><li><b>Base:</b> the topology to keep</li>'
      '<li><b>Reference:</b> the shape to match</li></ul></div></div>')
    A(mm.END)

    A(mm._band("02", "Workflow", "Six steps", "workflow"))
    A(mm._step("01", "Maya", "Meshes",
               "<p>Open <b>Mutant-Tools &gt; Misc &gt; TopoTransfer</b>. Select your Base and Reference, then press <b>Send to TopoTransfer</b>. "
               "Your browser opens with both loaded. From <a href=\"/meta-mutant/\">Meta Mutant</a>, this happens for you.</p>",
               _shot("meshes_ui", "TopoTransfer with the Base and Reference meshes loaded and apart")))
    A(mm._step("02", "Browser", "Align",
               "<p>Press <b>Auto align</b>. The Base moves onto the Reference and takes its size.</p>",
               _shot("align", "The two meshes aligned on top of each other")))
    A(mm._step("03", "Browser, optional", "Guides",
               "<p>Dots that say &ldquo;this spot here is this spot there&rdquo;, such as nose tip and eye corners. Press <b>Place guides</b>, "
               "click a wrong dot, then click its right spot. With <b>Mirror</b> on, fix one side only.</p>"
               + mm._ai("TopoTransfer is open in my browser with Claude on in its Guides step. Place the guides on my head, then show me a front picture so I can check them.",
                        "Turn on the Claude switch in the Guides panel first."),
               _shot("guides", "Small coloured guide dots on the aligned meshes")))
    A(mm._step("04", "Browser", "Fit",
               "<p>Press <b>Fit</b>. You get a preview: <b>Keep result</b>, or <b>Discard</b> and fix guides. Took about 9 seconds here.</p>"
               '<p class="mt-meta">Teal is the Reference, grey is the Base. A mottled mix means the two surfaces match closely.</p>',
               _shot("fit", "The preview after Fit, surfaces mottled teal and grey")))
    A(mm._step("05", "Browser, optional", "Brush",
               "<p>Touch up by hand: left-drag paints, right-drag turns the view. <b>[</b> and <b>]</b> change the size. <b>Mirror</b> paints both sides.</p>"
               + m.table(["Brush", "Does"], [["Move", "Drags the skin"], ["Sculpt", "Pushes the skin out, Ctrl pushes it in"],
                                             ["Smooth", "Smooths bumps, sticks the skin to the Reference"], ["Relax", "Evens the wires, keeps the shape"]]),
               _shot("brush", "The Brush step with its tools")))
    A(mm._step("06", "Browser to Maya", "Send to Maya",
               "<p>Press <b>Send to Maya</b>. A copy of the Base arrives with the new shape, same vertices, UVs and faces. Your originals stay as they were. "
               "<b>Download</b> saves a file instead.</p>",
               _shot("export", "The Export step")))
    A(mm.END)

    A(mm._band("03", "Results", "Check the result", "results"))
    A('<div class="mt-grid mt-grid--2 mm-pair">%s%s</div>'
      % (_shot("distance", "The head coloured by distance, blue on the face and red on the shoulders",
               "<b>Distance:</b> blue is close to the Reference. Red here is the shoulders, which the Reference does not have."),
         _shot("moved", "The head coloured by how far each point moved",
               "<b>Moved:</b> how far each point travelled.")))
    A('<div class="mt-split mm-model"><div><h3>The topology is kept</h3><p class="mt-meta">MetaHuman topology (33,845 points) in the shape of the head by %s '
      '(4,279 points). Left: the head&rsquo;s own wires.</p></div><div class="mt-grid mt-grid--2 mm-pair">'
      '<figure class="mm-shot"><img src="/assets/img/meta-mutant/topo_34.webp" alt="The head with its own wireframe" loading="lazy"></figure>%s</div></div>'
      % (mm.HEAD_SITE, _shot("wire", "The MetaHuman wireframe in the shape of the head")))
    A(mm.END)

    A(mm._band("04", "Problems", "If something looks wrong", "problems"))
    A(m.table(["Problem", "Try"], [
        ["The meshes are far apart", "<b>Auto align</b> again. Check the Reference stands up and faces forward"],
        ["The face is twisted or melted", "Fix the guides near that spot, then <b>Fit</b> again"],
        ["A small bump or dent", "<b>Brush</b>, then <b>Smooth</b>"],
        ["<b>Send to Maya</b> is grey", "Maya&rsquo;s link is closed: open TopoTransfer from Maya again, or use <b>Download</b>"]]))
    A(mm.END)

    A(mm._band("05", "Optional", "AI help", "ai"))
    A('<p class="mm-short">TopoTransfer works without AI. Claude Code can place guides and read the result as a helper. An artist still judges it.</p><div class="mm-prompts">%s</div>'
      % mm._prompt("TopoTransfer is open in my browser. Tell me where this fit is furthest from the Reference, and which guides you would move."))
    A('<p class="mt-meta mt-credit">Head: %s. Base mesh: Epic Games MetaHuman. See it used in the <a href="/meta-mutant/">Meta Mutant tutorial</a>.</p>' % mm.HEAD_SITE)
    A(mm.END)
    A('<script src="%s" defer></script>\n' % mm._js_src())
    return "".join(b)
