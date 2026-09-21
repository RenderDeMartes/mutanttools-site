# -*- coding: utf-8 -*-
"""Builds /maya-auto-rigger/ - the search landing page for 'maya auto rigger'.

Written to actually answer the query rather than repeat it: what an auto rigger
does, how a block-based one differs from a fixed-skeleton one, what it costs,
and how to get going in ten minutes. Carries SoftwareApplication, FAQPage,
HowTo and BreadcrumbList JSON-LD.
"""
import json
import mt_md as m

TOC = [
    ("what", "What an auto rigger does"),
    ("why-blocks", "Why block-based"),
    ("quickstart", "Rig a character in 10 minutes"),
    ("coverage", "What it rigs"),
    ("games", "Games and Unreal"),
    ("face", "Facial rigging"),
    ("python", "Scriptable"),
    ("compare", "How it compares"),
    ("requirements", "Requirements"),
    ("faq", "FAQ"),
]

FAQ = [
    ("Is Mutant Tools a free Maya auto rigger?",
     "Yes. Mutant Tools is free to download and the full source is public on GitHub. There is no "
     "licence server, no node-locked key and no watermark on the rigs it produces. You can use it "
     "on commercial work."),
    ("Which Maya versions does it support?",
     "Maya 2022 and newer are recommended. The codebase keeps Python 2 and Python 3 compatibility "
     "patterns, so older Maya releases generally load, but the tested target is 2022+."),
    ("Can I rig something other than a biped?",
     "Yes. Alongside the human templates there are blocks for quadrupeds, birds and wings, snakes, "
     "tails, insect legs, vehicles, props and cloth. Because the system is modular you can also "
     "combine blocks to rig anatomy no template covers."),
    ("Does the rig work in Unreal Engine or Unity?",
     "Yes. There are dedicated game blocks, a game-ready human template, a body converter and "
     "MetaHuman and DNA calibration utilities under the Unreal tools. Bind joints are kept as a "
     "clean, exportable hierarchy separate from the control rig."),
    ("What happens when I need to change a rig after animation has started?",
     "Blocks and guides are the source, the rig is the output. You change the guide or the block "
     "option and rebuild. Control shapes and skin weights can be saved and reapplied as part of "
     "the build through the data blocks, so a rebuild does not cost you that work."),
    ("Is it an auto rigger or a rigging framework?",
     "Both, and that is the point. Templates give you a complete character rig in a few clicks. "
     "Underneath, every block is a Python file calling a documented API, so a technical director "
     "can extend it or wire it into a pipeline instead of fighting a black box."),
    ("Can I write my own modules?",
     "Yes. A block is a folder with a JSON file describing its options and a Python file with a "
     "create and a build function. Drop it into the Blocks folder and the auto rigger picks it up "
     "with no registration step. The developer guide walks through a complete example."),
    ("Does it do facial rigging too?",
     "Yes. There are twenty facial blocks covering jaw, mouth, eyelids, brows, cheeks, nose, "
     "tongue, teeth, commissures, orbicularis, sticky lips and pupil dilation, plus face "
     "templates and a face install tool."),
]

STEPS = [
    ("Install", "Drag <code>easy_install.py</code> into a Maya viewport. It copies the tools into "
                "your scripts folder, installs the shelf and adds the Mutant-Tools menu so it "
                "loads on every start."),
    ("Open the auto rigger", "Mutant-Tools &rarr; Rigging &rarr; Open Autorigger."),
    ("Drop a template", "Pick a template - human, game-ready human, quadruped, bird, car, prop - "
                        "and the whole block stack appears in the outliner."),
    ("Place the guides", "Move the guides onto your mesh. This is the only genuinely manual step, "
                         "and it is the one that decides whether the rig is any good."),
    ("Set the options", "Each block has a config node: control shape and size, colour, mirror "
                        "behaviour, twist count, ribbons on or off, what it parents to."),
    ("Build", "Press build. Blocks run top to bottom in outliner order and produce the rig."),
    ("Iterate", "Adjust a guide or an option and build again. The rig is disposable; the blocks "
                "are what you keep."),
]


def _jsonld(stats):
    app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Mutant Tools",
        "applicationCategory": "DesignApplication",
        "applicationSubCategory": "3D rigging",
        "operatingSystem": "Windows, macOS, Linux",
        "softwareRequirements": "Autodesk Maya 2022 or newer",
        "description": ("Free block-based auto rigger and modular rigging framework for Autodesk "
                        "Maya. %d rigging blocks covering biped, facial, animal, vehicle, prop "
                        "and game rigs, with a documented Python API." % stats["blocks"]),
        "url": "https://mutanttools.com/maya-auto-rigger/",
        "downloadUrl": "https://github.com/RenderDeMartes/Mutant_Tools",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Organization", "name": "Blue Tape Rigging",
                   "url": "https://bluetaperigging.com/"},
        "featureList": [
            "Block-based modular rigging",
            "Non-destructive rebuilds from guides",
            "Biped, quadruped, bird, vehicle and prop templates",
            "Facial rigging modules",
            "Game-ready and Unreal Engine export",
            "Python API for pipeline integration",
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "How to auto rig a character in Maya with Mutant Tools",
        "totalTime": "PT10M",
        "tool": [{"@type": "HowToTool", "name": "Autodesk Maya 2022+"},
                 {"@type": "HowToTool", "name": "Mutant Tools"}],
        "step": [{"@type": "HowToStep", "position": i + 1, "name": n,
                  "text": m.re.sub(r"<[^>]+>", "", t)} for i, (n, t) in enumerate(STEPS)],
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Mutant Tools",
             "item": "https://mutanttools.com/"},
            {"@type": "ListItem", "position": 2, "name": "Maya auto rigger",
             "item": "https://mutanttools.com/maya-auto-rigger/"},
        ],
    }
    out = []
    for obj in (app, faq, howto, crumbs):
        out.append('<script type="application/ld+json">%s</script>'
                   % json.dumps(obj, ensure_ascii=False))
    return "\n".join(out)


def build(stats):
    b = []
    A = b.append

    A('<header class="mt-hero"><div class="mt-wrap">')
    A('<p class="mt-kicker">Free &middot; Open source &middot; Maya 2022+</p>')
    A('<h1>A Maya auto rigger that does not box you in</h1>')
    A('<p class="mt-lede">Mutant Tools is a free, block-based auto rigger for Autodesk Maya. '
      'Drop a template, place the guides, press build. Then keep going &mdash; every one of the '
      '%d blocks is a Python file you can read, change or replace.</p>' % stats["blocks"])
    A('<p><a class="mt-btn" href="https://github.com/RenderDeMartes/Mutant_Tools" target="_blank" '
      'rel="noopener">Download free</a>'
      '<a class="mt-btn mt-btn--ghost" href="#quickstart">See how it works</a></p>')
    A('<ul class="mt-stats">'
      '<li><b>%d</b><span>rigging blocks</span></li>'
      '<li><b>%d</b><span>categories</span></li>'
      '<li><b>%d</b><span>python commands</span></li>'
      '<li><b>$0</b><span>no licence</span></li></ul>'
      % (stats["blocks"], stats["categories"], stats["methods"]))
    A('</div></header>')

    A('<div class="mt-wrap"><div class="mt-layout">')
    A(m.toc(TOC))
    A('<article class="mt-body">')

    # ------------------------------------------------------------- what
    A(m.h2("What a Maya auto rigger actually does", "what"))
    A("<p>Rigging a character by hand is the same few hundred operations every time: duplicate a "
      "joint chain for IK and FK, build the switch, place a pole vector, add twist joints, make "
      "controls, colour them by side, zero them out, mirror the whole thing, wire the stretch, "
      "hide the channels animators must not touch. None of it is interesting the second time.</p>")
    A("<p>An auto rigger does that work from a description of where the joints go. You position "
      "guides on the mesh; the tool produces the joints, controls, constraints and utility nodes. "
      "A good one does it <b>repeatably</b> &mdash; delete the rig, change one guide, build again, "
      "and you get the same rig with one thing different.</p>")
    A(m.note("<p>That repeatability is the real feature. A rig you cannot rebuild is a rig you "
             "cannot fix once animation has started, which is exactly when the note arrives.</p>"))

    # -------------------------------------------------------- why blocks
    A(m.h2("Why block-based beats one big button", "why-blocks"))
    A("<p>Most auto riggers ship a fixed skeleton. They are quick until your character has a tail, "
      "four arms, a jaw that opens sideways or a wheel where a foot should be &mdash; and then you "
      "are outside the tool, hand-rigging the interesting part and hoping it survives the next "
      "rebuild.</p>")
    A("<p>Mutant Tools has no fixed skeleton. A rig is a stack of independent blocks, each owning "
      "one piece of anatomy:</p>")
    A(m.plain("""
        Mutant_Build
        |-- BaseA_Block          base hierarchy, global and gimbal controls
        |-- Spine_Block          IK/FK spline spine
        |-- L_Arm_Block          FK/IK limb, twist, ribbons
        |-- R_Arm_Block
        |-- L_Leg_Block
        |-- Head_Block
        |-- Jaw_Block
        `-- Tail_Block           because your character has one
        """, "outliner"))
    A("<p>Each block carries its own options on a config node and its own build function. They run "
      "top to bottom in outliner order, so reordering blocks reorders the build. Adding anatomy "
      "the authors never imagined means adding a block, not forking the tool.</p>")
    A(m.cards([
        ("Non-destructive", "Guides and blocks are the source. The rig is output. Rebuild as often "
                            "as the notes demand."),
        ("Composable", "Mix a biped spine with a quadruped limb and a vehicle wheel in one asset. "
                       "Nothing forbids it."),
        ("Readable", "Every block is a Python file in a folder. Nothing is compiled, nothing is "
                     "hidden, nothing phones home."),
        ("Extensible", "Write a block, drop it in the folder, it shows up in the UI. No plugin "
                       "registration, no rebuild."),
    ], 2))

    # -------------------------------------------------------- quickstart
    A(m.h2("Rig a character in 10 minutes", "quickstart"))
    A("<ol>")
    for name, text in STEPS:
        A("<li><b>%s.</b> %s</li>" % (name, text))
    A("</ol>")
    A(m.note("<p>Guide placement is where the craft is. The tool removes the typing, not the "
             "judgement &mdash; where the elbow actually bends and how the shoulder should behave "
             "is still your call, and it is still what separates a rig animators like from one "
             "they work around.</p>"))

    # ---------------------------------------------------------- coverage
    A(m.h2("What it rigs", "coverage"))
    A(m.table(["Category", "Blocks", "Covers"], [
        ["Presets", "19", "Whole-character templates: human, simple human, game human, Unreal "
                          "game human, toon, toon face, minotaur, quadruped, seagull, bird, "
                          "chameleon, tortoise, sloth, pig, car, prop, hero prop"],
        ["Biped", "17", "Spine and simple spine, clavicle and auto clavicle, pelvis, limb and "
                        "simple limb, head, hand and smart hand, foot and foot box, eyes, hair, "
                        "soft-IK legs"],
        ["Facial", "20", "Skull, jaw, mouth (standard, ribbon and games), eyelids, eyelashes, "
                         "nose, cheeks, brows, tongue, teeth, commissures, orbicularis, sticky "
                         "lips, pupil dilation"],
        ["Animals", "8", "Quadruped limb and spine, wings, tail, ant leg, snake, animal mouth"],
        ["Vehicles", "11", "Wheel and auto wheel, steering wheel, chassis, door, window, seat, "
                           "trunk, side mirror, drift, push"],
        ["Props", "15", "Single FK, chain, multi-bone, reverse FK, reverse spline, ribbonizer, "
                        "ribbon tweakers, squash, lattice, blendshape, rivet, slide, locals, "
                        "dynamic scale"],
        ["Clothes", "6", "Cap, cape, shirt, skirt, tie, pin"],
        ["Games", "3", "Game root, body converter, slide and push correctives"],
        ["Data", "2", "Reapply saved skin weights and control shapes during the build"],
        ["Studio", "17", "House conventions applied on every asset: orients, rotate orders, "
                         "pickwalking, visibility attributes, colour changes, defaults, renaming"],
        ["Other", "15", "Base rig, code and stop blocks, skinning, proxy attributes, space "
                        "switches, soft mods, surface constraints, joint labelling"],
    ]))
    A('<p><a href="/wiki/blocks/">Browse all %d blocks and their options &rarr;</a></p>' % stats["blocks"])

    # ------------------------------------------------------------- games
    A(m.h2("Games and Unreal Engine", "games"))
    A("<p>Game rigs have different rules: a clean joint hierarchy, a joint budget, no constraint "
      "spaghetti in the exported skeleton, and a control rig that never leaves Maya.</p>")
    A("<p>Mutant Tools keeps bind joints in their own group from the start, separate from the "
      "control rig, so the exportable skeleton is exactly what you want and nothing else. On top "
      "of that there are game-ready human templates, a body converter, corrective blocks for "
      "slide and push deformation, crowd tools, and MetaHuman and DNA calibration utilities under "
      "the Unreal side.</p>")

    # -------------------------------------------------------------- face
    A(m.h2("Facial rigging", "face"))
    A("<p>Twenty facial blocks, plus face templates and a dedicated face install tool. Jaw, mouth "
      "&mdash; standard, ribbon and a lighter games variant &mdash; eyelids, eyelashes, brows and "
      "advanced brows, cheeks and advanced cheeks, nose, tongue, teeth, commissures, orbicularis, "
      "sticky lips, pupil dilation, and post-build fixes.</p>")
    A("<p>Faces are where fixed-skeleton auto riggers fail hardest, because no two face designs "
      "agree. Blocks let you take the jaw and eyelid setups and leave the rest, or stack a "
      "ribbon mouth on a toon face without arguing with the tool.</p>")

    # ------------------------------------------------------------ python
    A(m.h2("Scriptable all the way down", "python"))
    A("<p>The UI is a thin layer. Everything it does is a call you can make yourself, which is "
      "what makes batch rebuilds, asset checks and pipeline integration possible.</p>")
    A(m.code("""
        from maya import cmds
        from Mutant_Tools.Utils.Rigging import main_mutant

        mt = main_mutant.Mutant()
        nc, curve_data, setup = mt.import_configs()

        # a full FK/IK limb with twist, in one call
        mt.twist_fk_ik(start='L_Shoulder_Jnt',
                       mid='L_Elbow_Jnt',
                       end='L_Wrist_Jnt',
                       size=4,
                       twist_amount=6)
        """, "python"))
    A("<p>There are %d documented commands on that object, covering controls and shapes, "
      "attributes, colour, FK and IK, twist, ribbons, spines, deformers, matrices, rivets, LODs "
      "and file IO.</p>" % stats["methods"])
    A('<p><a href="/developer/">Read the developer guide &rarr;</a> &middot; '
      '<a href="/wiki/commands/">Command reference &rarr;</a></p>')

    # ----------------------------------------------------------- compare
    A(m.h2("How it compares", "compare"))
    A(m.table(["", "Fixed-skeleton auto rigger", "Mutant Tools"], [
        ["Non-standard anatomy", "Rig it by hand outside the tool", "Add or write a block"],
        ["Changing a built rig", "Often a manual patch", "Change a guide or option, rebuild"],
        ["Source code", "Usually closed", "Public, readable Python"],
        ["Extending it", "Plugin API if you are lucky", "Drop a folder into <code>Blocks/</code>"],
        ["Pipeline integration", "Whatever is exposed", "Every command is public Python"],
        ["Naming conventions", "Usually fixed", "JSON config, fork it per studio"],
        ["Cost", "Per-seat licence, commonly", "Free, no licence server"],
    ]))
    A(m.note("<p>The honest trade: a fixed-skeleton rigger gets a standard biped standing up "
             "faster, because it asks fewer questions. Mutant Tools pays that back the first time "
             "a character is not standard, and on any show where rigs get rebuilt.</p>"))

    # ------------------------------------------------------ requirements
    A(m.h2("Requirements", "requirements"))
    A(m.table(["", ""], [
        ["Host", "Autodesk Maya 2022 or newer"],
        ["Python", "Python 3, with Python 2 compatibility retained in the codebase"],
        ["OS", "Windows, macOS, Linux &mdash; wherever Maya runs"],
        ["Licence", "Free, source public on GitHub"],
        ["Optional", "ngSkinTools v2, Brave Rabbit Shapes, Faceform Wrap &mdash; installable from "
                     "the Mutant-Tools menu"],
    ]))

    # --------------------------------------------------------------- faq
    A(m.h2("Frequently asked questions", "faq"))
    for q, a in FAQ:
        A(m.h3(q))
        A("<p>%s</p>" % a)

    A('<div class="mt-cta">'
      '<h2>Download Mutant Tools</h2>'
      '<p>Free, open source, and installed by dragging one file into Maya. If you are rigging '
      'something the templates do not cover, that is the case it was built for.</p>'
      '<a class="mt-btn" href="https://github.com/RenderDeMartes/Mutant_Tools" target="_blank" '
      'rel="noopener">Get it on GitHub</a>'
      '<a class="mt-btn mt-btn--ghost" href="/rigger/">For riggers</a>'
      '</div>')

    A('</article></div></div>')
    A(m.TOC_JS)
    return "".join(b), _jsonld(stats)
