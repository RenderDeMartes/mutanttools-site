# -*- coding: utf-8 -*-
"""The topic cluster around /maya-auto-rigger/.

One landing page does not rank for a head term on its own. These four cover the
adjacent searches people actually type - free tools, faces, animals, game rigs -
and each is written from what is really in the repo rather than padded with the
keyword. They link to each other and up to the auto-rigger page, which is the
structure that makes the head term winnable.

Anything thin enough to read as a doorway page was left out on purpose.
"""
import json
import mt_md as m

FAQ_SCHEMA = "https://schema.org"


def _faq_ld(pairs):
    return ('<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": FAQ_SCHEMA, "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs],
    }, ensure_ascii=False))


def _crumbs(name, path):
    return ('<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": FAQ_SCHEMA, "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Mutant Tools",
             "item": "https://mutanttools.com/"},
            {"@type": "ListItem", "position": 2, "name": "Maya auto rigger",
             "item": "https://mutanttools.com/maya-auto-rigger/"},
            {"@type": "ListItem", "position": 3, "name": name,
             "item": "https://mutanttools.com" + path},
        ],
    }, ensure_ascii=False))


SIBLINGS = [
    ("/maya-auto-rigger/", "Maya auto rigger", "The whole system: block-based rigging, templates, requirements."),
    ("/free-maya-rigging-tools/", "Free Maya rigging tools", "Everything in the box, and what each window is for."),
    ("/maya-facial-rigging/", "Maya facial rigging", "Twenty face modules, and the order to build them in."),
    ("/maya-animal-rigging/", "Maya animal rigging", "Quadrupeds, birds, wings, tails and snakes."),
    ("/game-character-rigging-maya/", "Game rigging in Maya", "Clean skeletons, Unreal export, MetaHuman."),
]


def _also(current):
    items = [(t, '%s <a href="%s">Open &rarr;</a>' % (d, p))
             for p, t, d in SIBLINGS if p != current]
    return m.h2("Related guides", "related") + m.cards(items, 2)


def _cta(title, text):
    return ('<div class="mt-cta"><h2>%s</h2><p>%s</p>'
            '<a class="mt-btn" href="https://github.com/RenderDeMartes/Mutant_Tools" '
            'target="_blank" rel="noopener">Download free</a>'
            '<a class="mt-btn mt-btn--ghost" href="/maya-auto-rigger/">How it works</a></div>'
            % (title, text))


def _open(kicker, h1, lede, stats_html, toc):
    b = ['<header class="mt-hero"><div class="mt-wrap">',
         '<p class="mt-kicker">%s</p>' % kicker,
         '<h1>%s</h1>' % h1,
         '<p class="mt-lede">%s</p>' % lede]
    if stats_html:
        b.append(stats_html)
    b.append('</div></header>')
    b.append('<div class="mt-wrap"><div class="mt-layout">')
    b.append(m.toc(toc))
    b.append('<article class="mt-body">')
    return "".join(b)


def _close():
    return '</article></div></div>' + m.TOC_JS


# ===================================================== free rigging tools
FREE_FAQ = [
    ("Is Mutant Tools really free?",
     "Yes. It is free to download, the source is public on GitHub, and there is no licence server "
     "or node-locked key. You can use it on commercial work."),
    ("What is included in the download?",
     "The auto rigger and its 133 rigging blocks, the rig tools window, guide placement helpers, "
     "proxy and skinning utilities, mocap retargeting, crowd tools, an animation loader, a "
     "versioning tool and a block builder for writing your own modules."),
    ("Do I need any other plugins?",
     "No, but three optional ones integrate and can be installed from the Mutant-Tools menu: "
     "ngSkinTools v2 for layered skinning, Brave Rabbit Shapes for correctives, and Faceform Wrap "
     "for wrapping face data."),
    ("How do I install it?",
     "Drag easy_install.py into a Maya viewport. It copies the tools into your scripts folder, "
     "installs the shelf and registers the Mutant-Tools menu so it loads on every startup."),
    ("Does it update itself?",
     "The menu checks the public GitHub releases API on startup and offers to download and install "
     "a newer version. Turn dev mode on to suppress that while you are editing the code."),
]

FREE_TOC = [("whats-free", "What free means here"), ("in-the-box", "What is in the box"),
            ("windows", "The tool windows"), ("rig-tools", "Rig Tools, tab by tab"),
            ("install", "Installing"), ("assets", "Free assets"),
            ("faq", "FAQ"), ("related", "Related guides")]


def free_tools(stats):
    b = [_open("Free &middot; Open source",
               "Free Maya rigging tools that do not expire",
               "Mutant Tools is a complete rigging toolset for Autodesk Maya, given away free with "
               "the source public. No licence server, no seat count, no watermark on the rigs it "
               "produces, and nothing that stops working if the download page ever goes away.",
               '<ul class="mt-stats">'
               '<li><b>%d</b><span>rigging blocks</span></li>'
               '<li><b>%d</b><span>python commands</span></li>'
               '<li><b>30</b><span>tool windows</span></li>'
               '<li><b>$0</b><span>forever</span></li></ul>' % (stats["blocks"], stats["methods"]),
               FREE_TOC)]
    A = b.append

    A(m.h2("What free means here", "whats-free"))
    A("<p>Plenty of rigging tools are free until they are not. This one is on GitHub under the "
      "author's own account, it never contacts a licence server, and the whole thing is readable "
      "Python you can fork. If the site disappeared tomorrow, your copy would keep working and "
      "you would still be able to fix it.</p>")
    A(m.note("<p>The only thing that phones home is the update check, which asks the public GitHub "
             "releases API whether there is a newer tag. Turn dev mode on and even that stops.</p>"))

    A(m.h2("What is in the box", "in-the-box"))
    A(m.table(["", "What you get"], [
        ["Auto rigger", "%d blocks across %d categories, plus 19 whole-character templates"
         % (stats["blocks"], stats["categories"])],
        ["Python API", "%d documented commands for controls, FK/IK, twist, ribbons, deformers "
         "and file IO" % stats["methods"]],
        ["Facial system", "20 face modules and a face install tool"],
        ["Game tools", "Game-ready templates, a body converter, correctives, crowds, Unreal and "
         "MetaHuman utilities"],
        ["Skinning", "Strict skinning, weight save and load, rivet-to-skin conversion"],
        ["Mocap", "HumanIK retargeting with maps for Mixamo, Rokoko and Radical"],
        ["Pipeline", "Versioning, file cleaning, variant management, an asset rigger and a Kanban board"],
    ]))

    A(m.h2("The tool windows", "windows"))
    A("<p>Everything hangs off the <b>Mutant-Tools</b> menu Maya grows after install.</p>")
    A(m.cards([
        ("Auto Rigger", "The main window. Add blocks, place guides, set options, build."),
        ("Rig Tools", "The day-to-day box: controls, skinning, renaming, correctives."),
        ("Helpers", "Small fixes that come up constantly while rigging."),
        ("Block Builder", "Scaffolds a new block so you do not write the JSON by hand."),
        ("Guide Placements", "Save and reload guide positions between assets."),
        ("Face Install", "Drops a full facial setup onto a head."),
        ("Proxy Maker", "Builds proxy geometry for fast playback."),
        ("Strict Skinning", "Skinning with joint limits enforced, for game budgets."),
        ("Games / Crowds", "Game conversion and crowd variation."),
        ("Anim Loader", "Load animation onto rigs, HumanIK included."),
        ("Variant Manager", "Multiple looks off one rig."),
        ("Versionize", "Versioned saves that follow a convention."),
        ("Zombinator", "Batch-processes scenes without opening each one."),
        ("Kanban", "A board inside Maya, for tracking a rigging list."),
        ("Notes", "Scene notes that travel with the file."),
        ("Code Reader", "Read the tool's own source without leaving Maya."),
    ], 3))

    A(m.h2("Rig Tools, tab by tab", "rig-tools"))
    A("<p>The window most riggers keep open all day. Five tabs:</p>")
    A(m.table(["Tab", "What lives there"], [
        ["<b>Ctrls</b>", "Create controls, swap shapes, recolour, mirror shapes, scale and rotate "
                         "CVs, save and load control shapes"],
        ["<b>Skin</b>", "Copy and paste weights, save and load, rivet-to-skin constraints, "
                        "skin transfer between meshes"],
        ["<b>Rename</b>", "Bulk renaming and search-and-replace across hierarchies, using the "
                          "naming convention config"],
        ["<b>Correctives</b>", "Push joints, quad locators, driven blend systems for deformation "
                               "fixes"],
        ["<b>Tools</b>", "The rest: joint orientation, labelling, pickwalking, visibility "
                         "attributes, proxy attributes"],
    ]))

    A(m.h2("Installing", "install"))
    A("<ol><li>Download or clone from GitHub.</li>"
      "<li>Unzip anywhere.</li>"
      "<li>Drag <code>easy_install.py</code> into a Maya viewport.</li></ol>")
    A("<p>That copies the package into <code>maya/&lt;version&gt;/scripts</code>, installs the "
      "Bluetape Rigging shelf and adds the Mutant-Tools menu to Maya's menu bar, loading on every "
      "start. There is a manual route in <code>INSTALLATION_GUIDE.txt</code> if the drag and drop "
      "does not work on your setup.</p>")
    A(m.note("<p>Maya 2022 or newer is the tested target. The code keeps Python 2 and 3 "
             "compatibility patterns, so older releases usually load.</p>"))

    A(m.h2("Free assets", "assets"))
    A('<p>Community rigs built with Mutant Tools are free to download and pull apart on the '
      '<a href="/free-assets/">free assets page</a>. Opening a finished rig and looking at how the '
      'blocks were stacked is the fastest way to understand the system.</p>')

    A(m.h2("Frequently asked questions", "faq"))
    for q, a in FREE_FAQ:
        A(m.h3(q)); A("<p>%s</p>" % a)

    A(_also("/free-maya-rigging-tools/"))
    A(_cta("Get the whole toolset",
           "One download, no account, no licence. Drag one file into Maya and it is installed."))
    A(_close())
    return "".join(b), _faq_ld(FREE_FAQ) + _crumbs("Free Maya rigging tools", "/free-maya-rigging-tools/")


# ============================================================ facial rigging
FACE_FAQ = [
    ("Does Mutant Tools do facial rigging?",
     "Yes. There are 20 facial blocks covering skull, jaw, mouth, eyelids, eyelashes, brows, "
     "cheeks, nose, tongue, teeth, commissures, orbicularis, sticky lips and pupil dilation, plus "
     "face templates and a dedicated face install tool."),
    ("Is it joint-based or blendshape-based?",
     "Joint-based, with blendshape and corrective support layered on. That keeps the result "
     "exportable to a game engine while still allowing shape-driven fixes where joints alone are "
     "not enough."),
    ("Can I use only the parts I need?",
     "Yes, and that is the usual case. Faces never agree on design, so blocks let you take the jaw "
     "and eyelid setups and leave the rest, or stack a ribbon mouth on a cartoon face without "
     "fighting a fixed template."),
    ("What is the difference between Mouth, RibbonMouth and MouthGames?",
     "Three mouth builds for three needs. Mouth is the standard setup. RibbonMouth drives the lips "
     "along a NURBS ribbon for smoother, more controllable shapes. MouthGames is a lighter build "
     "with a smaller joint count for real-time work."),
    ("Does it handle sticky lips?",
     "Yes, as its own block, applied after the mouth is built."),
]

FACE_TOC = [("why-faces", "Why faces break auto riggers"), ("modules", "The 20 face modules"),
            ("order", "The order to build in"), ("mouth", "Three mouths"),
            ("eyes", "Eyes, lids and lashes"), ("extras", "Correctives and wrapping"),
            ("games", "Faces for games"), ("faq", "FAQ"), ("related", "Related guides")]


def facial(stats):
    b = [_open("Facial rigging",
               "Maya facial rigging, module by module",
               "Twenty facial blocks that stack in whatever combination the character needs. "
               "Joint-based so the result exports, modular so a cartoon face and a realistic one "
               "can share the same tooling without either being a compromise.",
               '<ul class="mt-stats">'
               '<li><b>20</b><span>face modules</span></li>'
               '<li><b>3</b><span>mouth builds</span></li>'
               '<li><b>2</b><span>face templates</span></li>'
               '<li><b>Joint</b><span>based</span></li></ul>',
               FACE_TOC)]
    A = b.append

    A(m.h2("Why faces break auto riggers", "why-faces"))
    A("<p>Bodies are broadly the same shape. Two arms, one spine, a predictable number of fingers. "
      "That is why a fixed-skeleton auto rigger can get a biped standing up in one click.</p>")
    A("<p>Faces are not like that. A stylised character with four teeth and a hinge jaw and a "
      "realistic digital human share almost no topology, no joint count and no control philosophy. "
      "A fixed facial template either covers one of those well and the other badly, or covers both "
      "badly.</p>")
    A(m.note("<p>Modules sidestep the argument. Take the jaw. Take the eyelids. Skip the "
             "orbicularis if the face does not need it. Add sticky lips only when the shot "
             "demands it.</p>"))

    A(m.h2("The 20 face modules", "modules"))
    A(m.table(["Module", "What it builds"], [
        ["<code>Skull</code>", "The root of the face, everything else parents under it"],
        ["<code>Jaw</code>", "Jaw open, sideways and forward, with the pivot where it belongs"],
        ["<code>Mouth</code>", "The standard lip and mouth setup"],
        ["<code>RibbonMouth</code>", "Lips driven along a NURBS ribbon for smoother shapes"],
        ["<code>MouthGames</code>", "A lighter mouth with a smaller joint count"],
        ["<code>MouthPostBuilds</code>", "Fixes applied after the mouth exists"],
        ["<code>Commissures</code>", "The mouth corners, as their own controllable system"],
        ["<code>StickyLips</code>", "Lips that stay together as the jaw opens"],
        ["<code>Orbicularis</code>", "The ring muscle around the mouth"],
        ["<code>Eyelids</code>", "Upper and lower lids following the eyeball"],
        ["<code>Eyelashes</code>", "Lashes driven by the lids"],
        ["<code>PupilDilation</code>", "Pupil and iris scaling"],
        ["<code>Brows</code>", "Brow controls"],
        ["<code>BrowsAdvance</code>", "A denser brow setup with more shaping"],
        ["<code>Cheeks</code>", "Cheek raise and puff"],
        ["<code>CheeksAdvance</code>", "A denser cheek setup"],
        ["<code>Nose</code>", "Nose, nostrils and flare"],
        ["<code>Tongue</code>", "An FK or spline tongue chain"],
        ["<code>Teeth</code>", "Upper and lower teeth, parented correctly to jaw and skull"],
        ["<code>VisAttrs</code>", "Visibility switches so animators see only what they need"],
    ]))
    A('<p><a href="/wiki/blocks/#003-facial">Every facial block with its options &rarr;</a></p>')

    A(m.h2("The order to build in", "order"))
    A("<p>Blocks run top to bottom in the outliner, so the stacking order <i>is</i> the dependency "
      "order. Faces have a natural one:</p>")
    A(m.plain("""
        Skull_Block          the face root
        Jaw_Block            everything mouth-shaped hangs off the jaw
        Teeth_Block
        Tongue_Block
        Mouth_Block          or RibbonMouth / MouthGames
        Commissures_Block
        Orbicularis_Block
        Eyelids_Block
        Eyelashes_Block
        Brows_Block
        Cheeks_Block
        Nose_Block
        PupilDilation_Block
        StickyLips_Block     after the mouth exists
        MouthPostBuilds      fixes, last
        VisAttrs_Block       hide what animators should not see
        """, "outliner order"))
    A(m.warn("<p>Put <code>StickyLips</code> or <code>MouthPostBuilds</code> above the mouth block "
             "and they will build against nodes that do not exist yet. If a facial build fails "
             "with missing nodes, check the outliner order before anything else.</p>"))

    A(m.h2("Three mouths, and when to use which", "mouth"))
    A(m.cards([
        ("Mouth", "The default. Joint-driven lips with the control density most film and TV work "
                  "wants. Start here."),
        ("RibbonMouth", "Lips ride a NURBS ribbon, so shapes stay smooth through extreme poses. "
                        "Worth it on hero characters and anything doing heavy dialogue."),
        ("MouthGames", "Fewer joints, built to a budget. Use when the rig has to survive an engine "
                       "skeleton limit."),
    ], 3))

    A(m.h2("Eyes, lids and lashes", "eyes"))
    A("<p>The <code>Eyes</code> block, over in the biped category, builds the eyeballs and their "
      "aim. <code>Eyelids</code> then rides on top, following the eyeball surface so the lids keep "
      "contact as the eye rotates. <code>Eyelashes</code> is driven by the lids rather than "
      "skinned separately, so they never slide.</p>")
    A("<p><code>PupilDilation</code> is separate because not every show needs it, and when it does, "
      "it is usually animated on its own.</p>")

    A(m.h2("Correctives and wrapping", "extras"))
    A("<p>Joints get you most of the way. For the rest:</p>")
    A("<ul>"
      "<li><b>Push joints</b> and <b>quad locators</b>, from the correctives system, drive "
      "deformation from real rotation values rather than hand-keyed fixes.</li>"
      "<li><b>Blendshape</b> and <b>soft mod</b> blocks layer shape work on top.</li>"
      "<li>The <b>Wrap</b> utilities, including FACS and Skeletor helpers, transfer face data "
      "between meshes - useful when the model changes late and you do not want to redo the face."
      "</li>"
      "<li><b>Faceform Wrap</b> integrates if you have it, installable from the Mutant-Tools menu."
      "</li></ul>")

    A(m.h2("Faces for games", "games"))
    A('<p>Joint-based means exportable. Keep the bind joints in their own group, use '
      '<code>MouthGames</code> to stay inside a joint budget, and the face travels to an engine '
      'with the body. More on that in the '
      '<a href="/game-character-rigging-maya/">game rigging guide</a>.</p>')

    A(m.h2("Frequently asked questions", "faq"))
    for q, a in FACE_FAQ:
        A(m.h3(q)); A("<p>%s</p>" % a)

    A(_also("/maya-facial-rigging/"))
    A(_cta("Rig a face with it",
           "The face install tool drops a full setup on a head, then you keep or drop modules "
           "until it matches the character."))
    A(_close())
    return "".join(b), _faq_ld(FACE_FAQ) + _crumbs("Maya facial rigging", "/maya-facial-rigging/")


# ============================================================ animal rigging
ANIMAL_FAQ = [
    ("Can Mutant Tools rig quadrupeds?",
     "Yes. There is a quadruped limb block, a quadruped spine block and a quadruped template that "
     "drops the whole stack at once, plus finished templates for a pig, a sloth, a tortoise and a "
     "chameleon."),
    ("Does it handle wings?",
     "Yes, with two blocks: a wing module for a single wing and a wings block for the pair. There "
     "are also seagull and generic bird templates."),
    ("What about tails and snakes?",
     "A tail block handles tails of any length, and a snake block builds a long spline-driven body. "
     "Both use the same spline and ribbon systems as the biped spine."),
    ("Can I combine animal and human anatomy?",
     "Yes, and the minotaur template ships as proof. Blocks do not know or care what else is in "
     "the scene, so a human torso with digitigrade legs and a tail is just three kinds of block in "
     "one outliner."),
    ("Is there an insect or many-legged option?",
     "There is an ant leg block for insect-style limbs. For many legs you add the block once per "
     "limb rather than looking for a special mode."),
]

ANIMAL_TOC = [("problem", "Where fixed riggers stop"), ("blocks", "The animal blocks"),
              ("templates", "Animal templates"), ("quad", "Quadruped limbs and spine"),
              ("wings", "Wings and birds"), ("tails", "Tails and snakes"),
              ("mixing", "Mixing anatomy"), ("faq", "FAQ"), ("related", "Related guides")]


def animal(stats):
    b = [_open("Creatures &middot; Quadrupeds",
               "Maya animal rigging without a human skeleton in the way",
               "Quadruped limbs and spines, wings, tails, snakes and insect legs, as blocks you "
               "stack in whatever combination the creature needs. Eight animal templates ship "
               "ready to place, from a seagull to a sloth.",
               '<ul class="mt-stats">'
               '<li><b>8</b><span>animal blocks</span></li>'
               '<li><b>8</b><span>creature templates</span></li>'
               '<li><b>%d</b><span>blocks total</span></li>'
               '<li><b>Free</b><span>open source</span></li></ul>' % stats["blocks"],
               ANIMAL_TOC)]
    A = b.append

    A(m.h2("Where fixed riggers stop", "problem"))
    A("<p>Most auto riggers are biped riggers with a creature mode bolted on. They assume two arms, "
      "two legs, a spine that runs vertically and a pelvis at the bottom. A horse breaks the first "
      "three assumptions before you have placed a guide.</p>")
    A("<p>With blocks there is no skeleton to break. A quadruped is a spine block laid horizontally, "
      "four limb blocks, a neck, a head and a tail. Nothing in the system needs to know it is "
      "looking at a horse.</p>")

    A(m.h2("The animal blocks", "blocks"))
    A(m.table(["Block", "What it builds"], [
        ["<code>QuadLimb</code>", "A quadruped leg with the extra joint digitigrade anatomy needs"],
        ["<code>QuadSpine</code>", "A horizontal spline spine built for four-legged bodies"],
        ["<code>Wings</code>", "A pair of wings"],
        ["<code>WingModule</code>", "A single wing, for asymmetric or many-winged creatures"],
        ["<code>Tail</code>", "A spline tail of any length, with FK and IK control"],
        ["<code>Snake</code>", "A long spline-driven body"],
        ["<code>AntLeg</code>", "Insect-style limbs"],
        ["<code>AnimalMouth</code>", "A muzzle and jaw built for animal head shapes"],
    ]))
    A('<p><a href="/wiki/blocks/#004-animals">All animal blocks with their options &rarr;</a></p>')

    A(m.h2("Animal templates", "templates"))
    A("<p>Eight finished creature stacks. Drop one, place the guides, build.</p>")
    A(m.cards([
        ("Quadruped", "The generic four-legged base. Start here for anything mammalian."),
        ("Minotaur", "Human torso on digitigrade legs - the proof that anatomy mixes."),
        ("Pig", "A stocky quadruped with a short neck."),
        ("Sloth", "Long limbs, a hanging posture."),
        ("Tortoise", "A shell, and limbs that retract."),
        ("Chameleon", "Independent eyes and a grasping tail."),
        ("Seagull", "A bird with a full wing setup."),
        ("Bird", "The generic bird base."),
    ], 4))

    A(m.h2("Quadruped limbs and spine", "quad"))
    A("<p>A quadruped leg is not a human leg with an extra bend. The ankle sits high and the foot "
      "is long, so the control that reads as an ankle to an animator is in a different place from "
      "the joint that actually pivots. <code>QuadLimb</code> is built around that.</p>")
    A("<p><code>QuadSpine</code> is the biped spline spine reoriented for a horizontal body, with "
      "the stretch and volume behaviour that makes a back arch read correctly rather than "
      "telescoping.</p>")
    A(m.note("<p>Both take the same twist, ribbon and stretch options as their biped counterparts, "
             "because underneath they call the same kinematics helpers. Learning the biped limb "
             "teaches you the quadruped one.</p>"))

    A(m.h2("Wings and birds", "wings"))
    A("<p><code>Wings</code> builds a pair; <code>WingModule</code> builds one. Use the single "
      "module when the creature is asymmetric, has more than two wings, or when one wing is "
      "damaged and rigged differently - all three come up more often than you would think.</p>")
    A("<p>Feather control is the reason wings get their own module rather than being an arm with "
      "extra joints: the primaries and secondaries need to fan and fold together, which is a "
      "different problem from a limb.</p>")

    A(m.h2("Tails and snakes", "tails"))
    A("<p><code>Tail</code> handles anything from a stub to a prehensile rope. <code>Snake</code> "
      "is for when the tail <i>is</i> the character - a long spline body with enough controls to "
      "drive it end to end.</p>")
    A("<p>Both are spline-driven, so length is a guide decision rather than a code decision. Add "
      "guides, get a longer tail.</p>")

    A(m.h2("Mixing anatomy", "mixing"))
    A("<p>This is the part fixed riggers cannot do. Blocks have no opinion about what else is in "
      "the scene, so a creature can be:</p>")
    A(m.plain("""
        Mutant_Build
        |-- BaseA_Block
        |-- QuadSpine_Block      four-legged body
        |-- L_QuadLimb_Block     front legs
        |-- R_QuadLimb_Block
        |-- L_Limb_Block         but human arms
        |-- R_Limb_Block
        |-- Wings_Block          and wings
        |-- Tail_Block           and a tail
        |-- Head_Block
        `-- AnimalMouth_Block    with a muzzle
        """, "outliner"))
    A('<p>Nothing in the system objects. If you need anatomy no block covers, you '
      '<a href="/developer/#first-block">write one</a> - a block is a folder with a JSON and a '
      'Python file.</p>')

    A(m.h2("Frequently asked questions", "faq"))
    for q, a in ANIMAL_FAQ:
        A(m.h3(q)); A("<p>%s</p>" % a)

    A(_also("/maya-animal-rigging/"))
    A(_cta("Rig a creature",
           "Start from the quadruped or bird template, or stack blocks until the anatomy matches "
           "whatever you have been handed."))
    A(_close())
    return "".join(b), _faq_ld(ANIMAL_FAQ) + _crumbs("Maya animal rigging", "/maya-animal-rigging/")


# ============================================================= game rigging
GAME_FAQ = [
    ("Can I export a Mutant Tools rig to Unreal Engine?",
     "Yes. Bind joints live in their own group, separate from the control rig, from the moment the "
     "base hierarchy is created. That group is the skeleton you export, so nothing from the control "
     "rig follows it into the engine."),
    ("Is there a game-ready template?",
     "Two: a game human template and an Unreal game human template that matches the engine's "
     "expected skeleton conventions."),
    ("Does it work with MetaHuman?",
     "There are MetaHuman and DNA calibration utilities under the Unreal tools, for working with "
     "MetaHuman data inside Maya."),
    ("How do I keep the joint count down?",
     "Use the simple limb and simple spine blocks instead of the full ones, MouthGames instead of "
     "the standard mouth, and the strict skinning tool, which enforces a maximum influence count "
     "per vertex while you paint."),
    ("Does it handle corrective deformation for games?",
     "Yes. The push joint system drives corrective joints from real rotation values through "
     "matrix blending, so the correction bakes into the skeleton rather than needing a blendshape "
     "the engine has to evaluate."),
    ("Can it build crowds?",
     "There are crowd tools for generating variation across many characters, including facial "
     "variation."),
]

GAME_TOC = [("different", "What games change"), ("hierarchy", "The skeleton you export"),
            ("templates", "Game templates"), ("budget", "Staying inside a joint budget"),
            ("correctives", "Correctives that survive export"),
            ("unreal", "Unreal and MetaHuman"), ("crowds", "Crowds"),
            ("faq", "FAQ"), ("related", "Related guides")]


def game(stats):
    b = [_open("Games &middot; Unreal",
               "Game character rigging in Maya, built to export",
               "A game rig has different rules: a clean joint hierarchy, a joint budget, no "
               "constraint spaghetti in the exported skeleton, and a control rig that never leaves "
               "Maya. Mutant Tools separates those from the first block you build.",
               '<ul class="mt-stats">'
               '<li><b>2</b><span>game templates</span></li>'
               '<li><b>3</b><span>game blocks</span></li>'
               '<li><b>60</b><span>unreal scripts</span></li>'
               '<li><b>Free</b><span>commercial use</span></li></ul>',
               GAME_TOC)]
    A = b.append

    A(m.h2("What games change", "different"))
    A("<p>Film rigs can be as heavy as the machine allows. Every constraint, every ribbon, every "
      "corrective shape is fine, because the rig only ever has to work in Maya.</p>")
    A("<p>A game rig is two things at once: a control rig for the animator and a skeleton the "
      "engine will actually run. The second one has hard limits - a joint count, no constraints, "
      "no utility nodes, a specific naming and orientation convention - and the first one must not "
      "leak into it.</p>")

    A(m.h2("The skeleton you export", "hierarchy"))
    A("<p>The base hierarchy puts bind joints in their own group before any block builds:</p>")
    A(m.plain("""
        Asset Name_Grp
        |-- Ctrl_Grp                 the control rig, stays in Maya
        |-- Rig_Grp
        |   |-- Bind_Joints_Grp      <- this is what you export
        |   |-- Bind_Geo_Grp
        |   |-- Miscellaneous_Grp
        |   `-- Template_Grp
        `-- Extra_Geo_Grp
        """, "outliner"))
    A("<p>Blocks parent their deformation joints into <code>Bind_Joints_Grp</code> and their "
      "controls into <code>Ctrl_Grp</code>. The separation is structural, not a cleanup step you "
      "remember to do at the end.</p>")
    A(m.ok("<p>Export <code>Bind_Joints_Grp</code> and the bound geometry. Nothing from the control "
           "rig is inside it, so there is no constraint or utility node to strip.</p>"))

    A(m.h2("Game templates", "templates"))
    A(m.cards([
        ("Game human", "A biped built to game conventions from the start - lighter limbs, a "
                       "controlled joint count."),
        ("Unreal game human", "The same, matched to Unreal's expected skeleton naming and "
                              "orientation."),
        ("Game root", "The root motion joint games need, as its own block."),
        ("Convert body", "Turns an existing body rig into a game-ready one rather than starting "
                         "over."),
    ], 2))

    A(m.h2("Staying inside a joint budget", "budget"))
    A(m.table(["Instead of", "Use", "Why"], [
        ["<code>Limb</code>", "<code>SimpleLimb</code>", "Fewer twist joints, no ribbons"],
        ["<code>Spine</code>", "<code>SimpleSpine</code>", "A shorter chain"],
        ["<code>Mouth</code>", "<code>MouthGames</code>", "A lighter facial build"],
        ["<code>Hand</code>", "<code>SmartHand</code>", "Driven fingers, fewer controls to export"],
    ]))
    A("<p>Twist counts come off the block's config, so a limb can ship with two twist joints "
      "instead of six without touching code. <b>Strict Skinning</b> then enforces a maximum "
      "influence count per vertex while you paint, rather than telling you about it at export.</p>")

    A(m.h2("Correctives that survive export", "correctives"))
    A("<p>Blendshape correctives are expensive in an engine. The push joint system does it with "
      "joints instead: a reader locator on the driving joint, a quad locator converting rotation "
      "through euler-quaternion so it stays stable past 90 degrees, and a matrix blend driving a "
      "corrective joint's position, rotation and scale between two poses.</p>")
    A("<p>The result is a joint that moves correctly at a given angle. It is in the skeleton, so it "
      "exports, and the engine evaluates a transform rather than a shape.</p>")
    A("<p>The <code>SlidePushCorrectives</code> block builds these as part of a normal rig build.</p>")

    A(m.h2("Unreal and MetaHuman", "unreal"))
    A("<p>The Unreal side of the repo is the largest single utility area, with around sixty "
      "scripts. It covers the Unreal game template, MetaHuman work, and DNA calibration for "
      "reading and writing MetaHuman DNA files from Maya.</p>")
    A(m.note("<p>DNA calibration ships as a vendored third-party library with compiled "
             "dependencies, which is most of why the repository is large. You do not need it "
             "unless you are working with MetaHuman data.</p>"))

    A(m.h2("Crowds", "crowds"))
    A("<p>Crowd tools generate variation across many characters from one rig, facial variation "
      "included. Combined with the variant manager, one build can produce a population rather than "
      "a character.</p>")

    A(m.h2("Frequently asked questions", "faq"))
    for q, a in GAME_FAQ:
        A(m.h3(q)); A("<p>%s</p>" % a)

    A(_also("/game-character-rigging-maya/"))
    A(_cta("Build a game rig",
           "Start from the Unreal game template, or convert a body rig you already have."))
    A(_close())
    return "".join(b), _faq_ld(GAME_FAQ) + _crumbs("Game character rigging in Maya",
                                                   "/game-character-rigging-maya/")


PAGES = [
    ("free-maya-rigging-tools", free_tools,
     "Free Maya Rigging Tools - Complete Rigging Toolset, No Licence | Mutant Tools",
     "Mutant Tools is a free, open-source rigging toolset for Autodesk Maya: an auto rigger with "
     "%(blocks)d blocks, %(methods)d Python commands, skinning, mocap and crowd tools. No licence server."),
    ("maya-facial-rigging", facial,
     "Maya Facial Rigging - 20 Modular Face Rig Modules | Mutant Tools",
     "Modular facial rigging for Maya: jaw, mouth, eyelids, brows, cheeks, tongue, sticky lips and "
     "more as 20 stackable blocks. Joint-based, game-exportable, free and open source."),
    ("maya-animal-rigging", animal,
     "Maya Animal Rigging - Quadruped, Bird and Creature Rigs | Mutant Tools",
     "Rig quadrupeds, birds, wings, tails and snakes in Maya with modular blocks and 8 creature "
     "templates. Mix animal and human anatomy freely. Free and open source."),
    ("game-character-rigging-maya", game,
     "Game Character Rigging in Maya - Unreal-Ready Skeletons | Mutant Tools",
     "Build game character rigs in Maya with clean exportable skeletons, joint budgets, joint-based "
     "correctives and Unreal and MetaHuman tools. Free and open source."),
]
