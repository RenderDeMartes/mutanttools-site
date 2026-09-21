# -*- coding: utf-8 -*-
"""Builds /developer/ - the Python developer guide for Mutant Tools.

Everything here was read out of RenderDeMartes/Mutant_Tools at HEAD: the block
JSONs, the exec_* scripts, main_mutant/tools/kinematics/modules, the configs and
the AutoRigger's build loop. Where the docs and the code disagreed, the code won.
"""
import mt_md as m

TOC = [
    ("quickstart", "60-second quickstart"),
    ("mental-model", "The mental model"),
    ("the-mt-object", "The mt object"),
    ("configs", "nc, setup, curve_data"),
    ("anatomy", "Anatomy of a block"),
    ("lifecycle", "The build lifecycle"),
    ("first-block", "Write your first block"),
    ("controls", "Controls, shapes, colour"),
    ("attributes", "Attributes"),
    ("kinematics", "FK, IK, twist, ribbons"),
    ("mirroring", "Mirroring"),
    ("versioning", "Block versioning"),
    ("traps", "Traps that will bite you"),
    ("pipeline", "Pipeline integration"),
    ("ai", "Using AI on this codebase"),
    ("reference", "Where to go next"),
]


def build(stats):
    b = []
    A = b.append

    # ---------------------------------------------------------------- hero
    A('<header class="mt-hero"><div class="mt-wrap">')
    A('<p class="mt-kicker">Developer guide</p>')
    A('<h1>Mutant Tools for Python developers</h1>')
    A('<p class="mt-lede">Mutant Tools is a block-based modular rigging system for Maya. '
      'Everything the UI does, it does by calling Python you can call yourself. This page '
      'teaches the whole surface: the <code>mt</code> API, how a block is defined and built, '
      'and how to ship your own blocks into the system.</p>')
    A('<ul class="mt-stats">'
      '<li><b>%d</b><span>mt methods</span></li>'
      '<li><b>%d</b><span>shipped blocks</span></li>'
      '<li><b>%d</b><span>control shapes</span></li>'
      '<li><b>Maya 2022+</b><span>Python 2 &amp; 3</span></li>'
      '</ul>' % (stats["methods"], stats["blocks"], stats["curves"]))
    A('<p style="margin-top:2rem">'
      '<a class="mt-btn" href="/wiki/">Open the command wiki</a>'
      '<a class="mt-btn mt-btn--ghost" href="https://github.com/RenderDeMartes/Mutant_Tools" '
      'target="_blank" rel="noopener">Source on GitHub</a></p>')
    A('</div></header>')

    A('<div class="mt-wrap"><div class="mt-layout">')
    A(m.toc(TOC))
    A('<article class="mt-body">')

    # ---------------------------------------------------------- quickstart
    A(m.h2("60-second quickstart", "quickstart"))
    A("<p>Install by dragging <code>easy_install.py</code> into a Maya viewport. That copies the "
      "package into your <code>maya/&lt;version&gt;/scripts</code> folder, installs the shelf and "
      "registers the <b>Mutant-Tools</b> menu so it loads on every startup.</p>")
    A("<p>Then, in the Script Editor's Python tab:</p>")
    A(m.code("""
        from maya import cmds

        import Mutant_Tools
        from Mutant_Tools.Utils.Rigging import main_mutant

        mt = main_mutant.Mutant()
        nc, curve_data, setup = mt.import_configs()

        # a control, coloured, with an offset group above it
        ctrl = mt.controller(name='Hand', shape='hand', size=4, color='blue')
        print(ctrl)
        """, "maya script editor"))
    A(m.note("Constructing <code>Mutant()</code> has a side effect: if the scene has no "
             "<code>Mutant_Tools</code> node it creates one, stamped with the build date and "
             "version as locked string attributes. That node is how a scene remembers which "
             "version of the tools built it."))

    A(m.h3("Every block script starts the same way", "boilerplate"))
    A("<p>This header is the contract. The <code>try/except</code> around the import exists so a "
      "block can be run both as a loose script sitting in its own folder and as part of the "
      "installed package.</p>")
    A(m.code("""
        from __future__ import absolute_import
        from maya import cmds
        import json
        import os
        from pathlib import Path

        try:
            import importlib; from importlib import reload
        except ImportError:
            import imp; from imp import reload

        import Mutant_Tools
        import Mutant_Tools.Utils.Rigging
        from Mutant_Tools.Utils.Rigging import main_mutant
        reload(Mutant_Tools.Utils.Rigging.main_mutant)

        mt = main_mutant.Mutant()

        TAB_FOLDER = '008_Props'        # which Blocks/ category this lives in
        PYBLOCK_NAME = 'exec_my_thing'  # module name without the _vNNN suffix
        """, "exec_my_thing_v001.py"))

    # -------------------------------------------------------- mental model
    A(m.h2("The mental model", "mental-model"))
    A("<p>Three ideas carry the whole system. Get these and the rest is API surface.</p>")
    A(m.cards([
        ("1. A block is a container", "A Maya <code>dagContainer</code> named "
         "<code>&lt;Name&gt;_Block</code>, living under a <code>Mutant_Build</code> group. It holds the "
         "guides you place by hand. It is the thing an artist drags around."),
        ("2. A config is a network node", "A sibling <code>network</code> node named "
         "<code>&lt;Name&gt;_Config</code>. Every option an artist can set is an attribute on it, "
         "plus the strings that say how to rebuild the block."),
        ("3. Build is re-runnable", "Blocks and guides are the source. The rig is the output. "
         "Deleting the rig and rebuilding from the same blocks must give the same result - "
         "that is the whole point of the system."),
    ], 3))
    A("<p>So a scene mid-rig looks like this:</p>")
    A(m.plain("""
        Mutant_Build                     <- group, holds every block
        |-- L_Arm_Block                  <- dagContainer (the block)
        |   `-- L_Shoulder_Guide ...     <- guides you place
        |-- Spine_Block
        `-- Jaw_Block

        L_Arm_Config                     <- network node (the options)
        Spine_Config
        Jaw_Config

        Asset Name_Grp                   <- the rig the build produces
        |-- Ctrl_Grp
        |-- Rig_Grp
        |   |-- Bind_Joints_Grp
        |   |-- Bind_Geo_Grp
        |   |-- Miscellaneous_Grp
        |   `-- Template_Grp
        `-- Extra_Geo_Grp
        """, "outliner"))
    A("<p>That rig hierarchy comes from <code>mt.build_baseA()</code>, driven entirely by "
      "<code>rig_setup.json</code>. Change the JSON, every rig you build afterwards changes shape.</p>")

    # ------------------------------------------------------- the mt object
    A(m.h2("The mt object", "the-mt-object"))
    A("<p>There is one entry point and it is deep. <code>Mutant</code> inherits straight down a "
      "chain, so a single instance exposes everything:</p>")
    A(m.plain("""
        Mutant              main_mutant.py   version checks, GitHub updates
          \\-- Modules_class   modules.py       blocks, guides, base rig, dev mode
              \\-- Kinematics_class kinematics.py FK/IK, twist, ribbons, matrices
                  \\-- Tools_class   tools.py      controls, attrs, colour, nodes, JSON
        """, "method resolution order"))
    A(m.table(
        ["Class", "File", "Public methods", "What lives there"],
        [["<code>Tools_class</code>", "<code>Utils/Rigging/tools.py</code>", "61",
          "Controls and curve shapes, colour, attribute creation, offset groups, utility-node "
          "wiring, JSON read/write, matrix and mesh queries, push/corrective joints"],
         ["<code>Kinematics_class</code>", "<code>Utils/Rigging/kinematics.py</code>", "36",
          "FK chains, IK chains and stretch, pole vectors, FK/IK switching, twist, ribbons, "
          "spline spines, wires, squash and bend, LODs, rivets"],
         ["<code>Modules_class</code>", "<code>Utils/Rigging/modules.py</code>", "14",
          "<code>create_block</code>, guides, joint orientation, the base rig hierarchy, "
          "the name prompt, logging, dev mode"],
         ["<code>Mutant</code>", "<code>Utils/Rigging/main_mutant.py</code>", "6",
          "Local/online version compare, GitHub release check and in-place update"]]))
    A(m.note('The full signature list, with every argument and default, is in the '
             '<a href="/wiki/">command wiki</a>. It is generated from the source, so it '
             'cannot drift out of date.'))

    # ------------------------------------------------------------- configs
    A(m.h2("nc, setup, curve_data", "configs"))
    A("<p>One call returns all three config dictionaries. Call it at the top of every "
      "<code>create_</code> and <code>build_</code> function:</p>")
    A(m.code("nc, curve_data, setup = mt.import_configs()", "python"))
    A("<p>They are plain JSON under <code>Mutant_Tools/config/</code>, which means a studio can "
      "fork the naming convention without touching a line of rigging code.</p>")

    A(m.h3("nc - naming conventions", "nc"))
    A("<p>Never hardcode a suffix. Build names from <code>nc</code> and the same block produces "
      "<code>_Ctrl</code> at one studio and <code>_CTL</code> at the next.</p>")
    A(m.table(["Key", "Value", "Key", "Value"], [
        ["<code>nc['module']</code>", "<code>_Block</code>", "<code>nc['ctrl']</code>", "<code>_Ctrl</code>"],
        ["<code>nc['guide']</code>", "<code>_Guide</code>", "<code>nc['gimbal_ctrl']</code>", "<code>_Gimbal_Ctrl</code>"],
        ["<code>nc['joint']</code>", "<code>_Jnt</code>", "<code>nc['world_ctrl']</code>", "<code>_World_Ctrl</code>"],
        ["<code>nc['joint_bind']</code>", "<code>_Bnd</code>", "<code>nc['group']</code>", "<code>_Grp</code>"],
        ["<code>nc['joint_end']</code>", "<code>_JntEnd</code>", "<code>nc['locator']</code>", "<code>_Loc</code>"],
        ["<code>nc['joint_twist']</code>", "<code>_JntTwist</code>", "<code>nc['curve']</code>", "<code>_Crv</code>"],
        ["<code>nc['ik']</code>", "<code>_Ik_Jnt</code>", "<code>nc['offset']</code>", "<code>_Offset</code>"],
        ["<code>nc['fk']</code>", "<code>_Fk_Jnt</code>", "<code>nc['root']</code>", "<code>_Root</code>"],
        ["<code>nc['left']</code>", "<code>L_</code>", "<code>nc['auto']</code>", "<code>_Auto</code>"],
        ["<code>nc['right']</code>", "<code>R_</code>", "<code>nc['null']</code>", "<code>_Null</code>"],
        ["<code>nc['center']</code>", "<code>C_</code>", "<code>nc['follicle']</code>", "<code>_Fol</code>"],
        ["<code>nc['geo']</code>", "<code>_Geo</code>", "<code>nc['skin_cluster']</code>", "<code>_Skin</code>"],
    ]))
    A("<p>Utility nodes have entries too - <code>nc['multiplyDivide']</code>, "
      "<code>nc['condition']</code>, <code>nc['blend']</code>, <code>nc['remap_value']</code>, "
      "<code>nc['reverse']</code>, <code>nc['unitConversion']</code>, <code>nc['distance']</code> - "
      "so even the plumbing in a rig reads consistently.</p>")

    A(m.h3("setup - rig defaults", "setup"))
    A(m.table(["Key", "Default", "Used for"], [
        ["<code>setup['base_groups']</code>", "<code>{geometry: Extra_Geo, control: Ctrl, rig: Rig}</code>",
         "Top level of every rig"],
        ["<code>setup['rig_groups']</code>", "<code>{bind_joints, bind_geo, misc, template}</code>",
         "Children of <code>Rig_Grp</code>"],
        ["<code>setup['main_ctrl_grp']</code>", "<code>Rig_Ctrl</code>", "Group parented under the gimbal control"],
        ["<code>setup['twist_axis']</code>", "<code>X</code>", "Default aim axis for twist and limbs"],
        ["<code>setup['secondaryAxisOrient']</code>", "<code>zup</code>", "Joint orientation up axis"],
        ["<code>setup['ik_fk_method']</code>", "<code>blend</code>", "<code>blend</code> or constraint switching"],
        ["<code>setup['left_color']</code> / <code>right_color</code>", "<code>blue</code> / <code>red</code>", "Side colouring"],
        ["<code>setup['main_color']</code>", "<code>lightBlue</code>", "Default control colour"],
        ["<code>setup['fk_ctrl']</code>", "<code>circlePointIn</code>", "Default FK shape"],
        ["<code>setup['ik_ctrl']</code> / <code>pv_ctrl']</code>", "<code>cube</code> / <code>sphere</code>", "Default IK and pole-vector shapes"],
        ["<code>setup['stretch_default']</code>", "<code>1</code>", "Stretch on by default"],
        ["<code>setup['volume_preservation']</code>", "<code>0.5</code>", "Squash amount on stretchy limbs"],
    ]))

    A(m.h3("curve_data - the shape library", "curve_data"))
    A("<p>%d named shapes, stored as raw CV positions and degree. Pass the name to "
      "<code>mt.curve()</code>, <code>mt.controller()</code> or "
      "<code>mt.change_curve_shape()</code>:</p>" % stats["curves"])
    A('<p style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.82rem;'
      'color:var(--mt-dim);line-height:2">%s</p>'
      % " &middot; ".join("<code>%s</code>" % c for c in stats["curve_names"]))

    # ------------------------------------------------------------- anatomy
    A(m.h2("Anatomy of a block", "anatomy"))
    A("<p>A block is a folder under <code>Blocks/&lt;category&gt;/</code> holding four files:</p>")
    A(m.plain("""
        Blocks/008_Props/01_Single_FK/
        |-- 01_Single_FK.json          <- launcher, never versioned
        |-- 01_Single_FK_v001.json     <- the versioned copy
        |-- exec_single_fk.py          <- legacy alias
        `-- exec_single_fk_v001.py     <- the implementation
        """, "folder layout"))
    A("<p>The launcher JSON keeps a stable filename and points at whichever version is live. "
      "That indirection is what lets an old scene keep rebuilding after you ship a v002.</p>")
    A(m.code("""
        {
            "Name":         "Single_FK",
            "Description":  "This will create a Single FK Ctrl + Joint",
            "Icon":         "Bone.png",
            "Enable":       "True",
            "python_file":  "exec_single_fk_v001.py",
            "import":       "import exec_single_fk_v001",
            "imp.reload":   "reload(exec_single_fk_v001)",
            "exec_command": "exec_single_fk_v001.create_single_fk_block()",
            "build_command":"exec_single_fk_v001.build_single_fk_block()",
            "attrs": {
                "CtrlType_enum":   "sphere:cube:square:octagon",
                "CtrlSize_float":  "4",
                "CtrlColor_enum":  "lightBlue:blue:white:purple",
                "Mirror_enum":     "False:True:Right_Only",
                "Gimbal_bool":     "True",
                "CreateJoint_bool":"True",
                "SetCtrlParentHierarchy_string": "Ctrl_Grp",
                "Help_string":     "Overview: ...  How To Use: ..."
            }
        }
        """, "01_Single_FK.json"))

    A(m.h3("The attrs dictionary and its type suffixes", "attr-suffixes"))
    A("<p><code>mt.create_block()</code> walks <code>attrs</code> and turns each key into a real "
      "Maya attribute on the config node. The suffix picks the type, and the suffix is stripped "
      "from the attribute name - <code>CtrlSize_float</code> becomes <code>.CtrlSize</code>.</p>")
    A(m.table(["Suffix", "Becomes", "Value in JSON", "Read it back with"], [
        ["<code>_string</code>", "string attribute", '<code>"Ctrl_Grp"</code>',
         "<code>cmds.getAttr(cfg + '.Name')</code>"],
        ["<code>_enum</code>", "enum attribute", '<code>"a:b:c"</code> (colon separated)',
         "<code>cmds.getAttr(cfg + '.Name', asString=True)</code>"],
        ["<code>_float</code>", "<b>integer</b>, min 1, max 20", '<code>"4"</code>',
         "<code>cmds.getAttr(cfg + '.Name')</code>"],
        ["<code>_bool</code>", "boolean attribute", '<code>"True"</code>',
         "<code>cmds.getAttr(cfg + '.Name')</code>"],
    ]))
    A(m.warn("<p><code>_float</code> does not create a float. It calls "
             "<code>new_attr_interger(min=1, max=20, default=int(value))</code>, so you get an "
             "<b>integer clamped between 1 and 20</b>. A control size of <code>4.5</code> is "
             "impossible and a twist count of <code>30</code> silently clamps to 20. If you need "
             "a real float, add it yourself with <code>mt.new_attr()</code> after "
             "<code>create_block</code> returns.</p>"))
    A(m.warn("<p>The type is chosen with <code>if 'string' in attr</code>, a <b>substring</b> test, "
             "not a suffix test, and it is checked in the order string, enum, float, bool. So an "
             "attribute you name <code>UseStringy_bool</code> contains <code>string</code> and "
             "quietly becomes a string attribute. Keep the type word out of the descriptive part "
             "of the name.</p>", "Sharp edge"))

    A(m.h3("What create_block gives you", "create-block-return"))
    A(m.code("""
        block, config = mt.create_block(
            name='L_Arm',
            icon='Limb',                 # resolves to Mutant_Tools/Icons/Limb.png
            attrs=module['attrs'],
            build_command=module['build_command'],
            import_command=module['import'],
        )
        # block  -> 'L_Arm_Block'   a dagContainer parented under 'Mutant_Build'
        # config -> 'L_Arm_Config'  a network node holding every option
        """, "python"))
    A("<p>On top of your own attributes, the config node always carries four more:</p>")
    A(m.table(["Attribute", "Locked", "Purpose"], [
        ["<code>precode</code>", "no", "Python (or MEL) run <b>before</b> this block builds"],
        ["<code>Import_Command</code>", "yes", "The <code>import ...</code> line the builder execs"],
        ["<code>Build_Command</code>", "yes", "The call the builder evals to build this block"],
        ["<code>postcode</code>", "no", "Python (or MEL) run <b>after</b> this block builds"],
    ]))
    A(m.note("<p><code>precode</code> and <code>postcode</code> are the escape hatch. A rigger who "
             "needs one odd fix on one asset can type it straight onto the block instead of "
             "forking your code. Both are <code>exec</code>'d, and if that raises, the builder "
             "falls back to <code>mel.eval</code> - so legacy MEL snippets keep working.</p>"))

    # ----------------------------------------------------------- lifecycle
    A(m.h2("The build lifecycle", "lifecycle"))
    A("<p>Pressing <b>Build</b> walks the blocks under <code>Mutant_Build</code> "
      "<b>in outliner order</b> and runs the same seven steps on each. Reordering blocks in the "
      "outliner reorders the build - that is the dependency system.</p>")
    A(m.plain("""
        for block in blocks:                      # outliner order, top to bottom
            cmds.select(block)
            config = config_of(block)

            exec(config.Import_Command)           # import exec_single_fk_v001
            exec(reload_command)                  # reload(exec_single_fk_v001)

            cmds.select(block)
            exec(config.precode)                  # falls back to mel.eval on error

            cmds.select(block)
            recipe = eval(config.Build_Command)   # <- your build_*() runs here
            recipes[block_name] = recipe          # return value is kept

            cmds.select(block)
            exec(config.postcode)
        """, "AutoRigger build loop, simplified"))

    A(m.ok("<p>Notice <code>cmds.select(block)</code> before every phase. <b>That is the calling "
           "convention.</b> Your <code>build_*()</code> takes no arguments; it finds its own block "
           "with <code>cmds.ls(sl=True)</code>. Always guard it - the selection can still be "
           "empty if someone calls your function by hand.</p>"))
    A(m.code("""
        def build_my_thing_block():
            nc, curve_data, setup = mt.import_configs()
            mt.check_is_there_is_base()

            selection = cmds.ls(sl=True) or []
            if not selection:
                cmds.warning('Select a block to build.')
                return

            block = selection[0]
            if not cmds.objExists(block):
                cmds.warning('Block does not exist: {}'.format(block))
                return
        """, "the guard every build function needs"))

    A(m.h3("The return value is not thrown away", "recipes"))
    A("<p>Whatever <code>build_*()</code> returns is stored in the builder's recipe dictionary "
      "under the block's name. Return a dict of the nodes you created and a later block can look "
      "them up instead of guessing at string names.</p>")
    A(m.code("""
        def build_my_thing_block():
            ...
            return {
                'ctrl': ctrl,
                'joint': jnt,
                'bind_joint': bind,
                'root': root,
            }
        """, "python"))

    A(m.h3("Deferring a block", "deferring"))
    A("<p>Two optional boolean attributes on the config change when a block runs:</p>")
    A(m.table(["Attribute", "Effect"], [
        ["<code>RunBeforeBuild</code>", "Block is pulled out of the normal pass and run first"],
        ["<code>RunAfterBuild</code>", "Block is deferred and run once every other block is done"],
    ]))
    A(m.note("<p>When either is on, the builder <b>skips that block's precode and postcode</b> "
             "during the main pass. Put the work in the build function, not in the code "
             "attributes, for any block that defers.</p>"))

    A(m.h3("check_is_there_is_base", "base"))
    A("<p>First line of every build function. It looks for the base rig hierarchy and calls "
      "<code>mt.build_baseA()</code> to create it if missing, so a block can never build into "
      "an empty scene and leave nodes at the root.</p>")
    A(m.code("mt.check_is_there_is_base()   # default base='BaseA'", "python"))

    # --------------------------------------------------------- first block
    A(m.h2("Write your first block", "first-block"))
    A("<p>A complete, working block - a single FK control with an optional joint. Drop the folder "
      "into <code>Blocks/008_Props/</code> and it appears in the AutoRigger with no registration "
      "step: the UI scans the folders.</p>")

    A(m.h3("1. The JSON", "first-json"))
    A(m.code("""
        {
            "Name":          "Beacon",
            "Description":   "A single control with an optional bind joint",
            "Icon":          "Bone.png",
            "Enable":        "True",
            "python_file":   "exec_beacon_v001.py",
            "import":        "import exec_beacon_v001",
            "imp.reload":    "reload(exec_beacon_v001)",
            "exec_command":  "exec_beacon_v001.create_beacon_block()",
            "build_command": "exec_beacon_v001.build_beacon_block()",
            "attrs": {
                "CtrlType_enum":  "sphere:cube:circleY:locator",
                "CtrlSize_float": "4",
                "CtrlColor_enum": "yellow:blue:red:lightBlue",
                "CreateJoint_bool": "True",
                "SetParent_string": "Ctrl_Grp",
                "Help_string": "Overview:\\n  One control, one optional joint.\\n\\nFields:\\n- CtrlType: the shape.\\n- CtrlSize: 1-20.\\n- CreateJoint: also make a bind joint."
            }
        }
        """, "99_Beacon.json"))
    A(m.note("<p><code>Help_string</code> is what the artist reads in the AutoRigger's help panel. "
             "Every shipped block has one. Write it for the person placing guides at 11pm, not "
             "for yourself.</p>"))

    A(m.h3("2. The create function", "first-create"))
    A("<p><code>create_</code> runs when an artist adds the block. It must be cheap and build "
      "nothing but the block, its config and its guides.</p>")
    A(m.code("""
        import os, json
        from pathlib import Path
        from maya import cmds

        import Mutant_Tools
        from Mutant_Tools.Utils.Rigging import main_mutant
        mt = main_mutant.Mutant()

        TAB_FOLDER = '008_Props'
        PYBLOCK_NAME = 'exec_beacon'


        def _module():
            path = os.path.join(os.path.dirname(__file__), '99_Beacon.json')
            with open(path) as handle:
                return json.load(handle)


        def create_beacon_block(name='Beacon'):
            nc, curve_data, setup = mt.import_configs()
            module = _module()

            name = mt.ask_name(text=name)
            if not name:
                cmds.warning('Cancelled.')
                return ''

            if cmds.objExists('{}{}'.format(name, nc['module'])):
                cmds.warning('Name already exists.')
                return ''

            block, config = mt.create_block(
                name=name,
                icon='Bone',
                attrs=module['attrs'],
                build_command=module['build_command'],
                import_command=module['import'],
            )

            # the guide the artist positions
            guide = cmds.spaceLocator(n=name + nc['locator'])[0]
            cmds.parent(guide, block)

            cmds.select(block)
            print('{} created.'.format(name))
        """, "exec_beacon_v001.py"))

    A(m.h3("3. The build function", "first-build"))
    A("<p><code>build_</code> reads the config, reads the guide, and produces rig. Every scene "
      "operation is guarded, every name comes from <code>nc</code>, and the new attribute is read "
      "through <code>attributeQuery</code> so a scene saved before you added it still builds.</p>")
    A(m.code("""
        def build_beacon_block():
            nc, curve_data, setup = mt.import_configs()
            mt.check_is_there_is_base()

            selection = cmds.ls(sl=True) or []
            if not selection:
                cmds.warning('Select the Beacon block to build.')
                return

            block = selection[0]
            name = block.replace(nc['module'], '')
            config = '{}_Config'.format(name)

            if not cmds.objExists(config):
                cmds.warning('No config for {}'.format(block))
                return

            guide = '{}{}'.format(name, nc['locator'])
            if not cmds.objExists(guide):
                cmds.warning('Guide missing: {}'.format(guide))
                return

            # ---- read options, every one defensively --------------------
            shape = cmds.getAttr('{}.CtrlType'.format(config), asString=True)
            size = cmds.getAttr('{}.CtrlSize'.format(config))
            color = cmds.getAttr('{}.CtrlColor'.format(config), asString=True)

            make_joint = True
            if cmds.attributeQuery('CreateJoint', node=config, exists=True):
                make_joint = cmds.getAttr('{}.CreateJoint'.format(config))

            parent_to = setup['base_groups']['control'] + nc['group']
            if cmds.attributeQuery('SetParent', node=config, exists=True):
                wanted = cmds.getAttr('{}.SetParent'.format(config))
                if wanted and cmds.objExists(wanted):
                    parent_to = wanted

            # ---- build ---------------------------------------------------
            ctrl = mt.curve(input=guide, type=shape, rename=True, custom_name=True,
                            name=name + nc['ctrl'], size=size)
            mt.assign_color(input=ctrl, color=color)

            root = mt.root_grp(input=ctrl)[0]

            # root_grp reparents ctrl, so the old DAG path can be stale
            ctrl = cmds.listRelatives(root, children=True, type='transform')[0]
            mt.match(root, guide, t=True, r=True)

            if cmds.objExists(parent_to):
                cmds.parent(root, parent_to)

            jnt = None
            if make_joint:
                cmds.select(clear=True)
                jnt = cmds.joint(n=name + nc['joint_bind'])
                mt.match(jnt, ctrl, t=True, r=True)
                cmds.parentConstraint(ctrl, jnt, mo=True)

                bind_grp = setup['rig_groups']['bind_joints'] + nc['group']
                if cmds.objExists(bind_grp):
                    cmds.parent(jnt, bind_grp)

            print('Built {}'.format(block))
            return {'ctrl': ctrl, 'root': root, 'joint': jnt}
        """, "exec_beacon_v001.py"))

    # ------------------------------------------------------------ controls
    A(m.h2("Controls, shapes, colour", "controls"))
    A(m.h3("Two ways to make a control", "control-ways"))
    A("<p><code>mt.controller()</code> is the modern one: it makes the curve, colours it, adds a "
      "gimbal child and a world offset in a single call. <code>mt.curve()</code> is the older, "
      "lower-level one and is still what most shipped blocks use, because it can convert an "
      "existing guide in place.</p>")
    A(m.code("""
        # modern: one call, gimbal and world offset included
        ctrl = mt.controller(input='', name='Hand', shape='hand',
                             color='blue', size=4, gimbal=True, world=True)

        # classic: turn a guide into a control, keeping its transform
        ctrl = mt.curve(input=guide, type='cube', rename=True, custom_name=True,
                        name=joint.replace(nc['joint'], nc['ctrl']), size=size)
        mt.assign_color(input=ctrl, color='blue')
        root = mt.root_grp(input=ctrl)[0]
        """, "python"))

    A(m.h3("Offset groups", "offset-groups"))
    A("<p><code>mt.root_grp()</code> inserts zeroed groups above a node, keeping its world "
      "transform and its place in the hierarchy. It returns a <b>list</b>.</p>")
    A(m.table(["Call", "Creates"], [
        ["<code>mt.root_grp(input=ctrl)</code>", "<code>Hand_Ctrl_Offset_Grp</code>"],
        ["<code>mt.root_grp(input=ctrl, autoRoot=True)</code>",
         "<code>Hand_Ctrl_Root_Grp</code> and <code>Hand_Ctrl_Auto_Grp</code>"],
        ["<code>mt.root_grp(input=ctrl, custom=True, custom_name='SdkBuffer')</code>",
         "<code>Hand_CtrlSdkBuffer_Grp</code>"],
    ]))
    A(m.warn("<p>Two things bite here. First, calling it twice with defaults tries to create the "
             "same name twice - always pass <code>custom=True, custom_name='...'</code> when a "
             "control gets more than one offset. Second, it <b>reparents the node</b>, so any DAG "
             "path you were holding may now be stale. Re-fetch the child from the returned group, "
             "exactly as the shipped <code>Single_FK</code> block does.</p>"))
    A(m.code("""
        root = mt.root_grp(input=ctrl)[0]
        ctrl = cmds.listRelatives(root, children=True, type='transform')[0]   # refresh
        """, "python"))

    A(m.h3("Colour", "colour"))
    A("<p><code>mt.assign_color()</code> takes ten names and sets Maya's index override. "
      "<code>mt.assign_color_rgb()</code> takes RGB or HSV. <code>mt.smart_assign_color()</code> "
      "picks by side from the name.</p>")
    A(m.table(["Name", "Index", "Name", "Index", "Name", "Index"], [
        ["<code>red</code>", "13", "<code>blue</code>", "6", "<code>white</code>", "16"],
        ["<code>purple</code>", "9", "<code>green</code>", "14", "<code>lightBlue</code>", "18"],
        ["<code>yellow</code>", "17", "<code>pink</code>", "20", "<code>grey</code>", "1"],
        ["<code>orange</code>", "21", "", "", "", ""],
    ]))
    A("<p>The convention the shipped blocks follow, driven from <code>setup</code>:</p>")
    A(m.code("""
        if side_guide.startswith(nc['right']):
            color = setup['right_color']        # red
        elif side_guide.startswith(nc['left']):
            color = setup['left_color']         # blue
        else:
            color = setup['center_color']       # yellow

        mt.assign_color(input=ctrl, color=color)
        """, "python"))

    # ---------------------------------------------------------- attributes
    A(m.h2("Attributes", "attributes"))
    A("<p>Use the <code>mt</code> helpers rather than <code>cmds.addAttr</code>. They keep "
      "ordering, keyability and locking consistent across every rig the system produces.</p>")
    A(m.table(["Call", "Makes"], [
        ["<code>mt.new_attr(input, name, min, max, default, keyable)</code>", "A double"],
        ["<code>mt.new_attr_interger(input, name, min, max, default)</code>", "An integer"],
        ["<code>mt.new_enum(input, name, enums='Hide:Show', default)</code>", "An enum"],
        ["<code>mt.new_boolean(input, name, dv='True')</code>", "A boolean"],
        ["<code>mt.string_attr(input, name, string)</code>", "A string, for storing data on the rig"],
        ["<code>mt.line_attr(input, name, lines=10)</code>", "A separator row in the channel box"],
        ["<code>mt.hide_attr(input, t, r, s, v, rotate_order, show)</code>", "Hides or reveals channels"],
        ["<code>mt.create_proxy_attr(original_attr, output_node, ...)</code>", "A proxy of an attribute elsewhere"],
        ["<code>mt.change_default(attr, default)</code>", "Changes an existing attribute's default"],
    ]))
    A(m.code("""
        # a roll attribute with a sane range
        attr = mt.new_attr(input=ik_attrs_shape, name='Roll', min=-100, max=100, default=0)

        # a visibility switch
        mt.new_enum(input=ctrl, name='Gimbal', enums='Hide:Show')

        # a labelled divider, then hide what animators must not touch
        mt.line_attr(input=ctrl, name='Extras')
        mt.hide_attr(input=jaw_ctrl, s=True, v=True)
        """, "python"))

    A(m.h3("Wiring values without spaghetti", "wiring"))
    A("<p>Rather than hand-building utility nodes, the <code>mt</code> helpers name them from "
      "<code>nc</code> and connect both sides in one call.</p>")
    A(m.code("""
        # invert a value into a rotation limit
        mt.connect_md_node(in_x1=up_limit, in_x2=-1, mode='multiply',
                           out_x=upper_pivot_joint + '.minRotLimit.minRotZLimit')

        # remap one range onto another
        mt.connect_remap_value(input_value, output_value, value=0)

        # insert an addDoubleLinear between two already-connected plugs
        mt.replace_connection_with_doublelinear(input=node, attr='translateY')

        # matrix parenting instead of a constraint
        mt.parent_matrix(this=driver, that=driven, translate=True, rotate=True, scale=False)
        """, "python"))
    A(m.note("<p><code>mt.create_add_double_linear()</code> and "
             "<code>mt.create_mdl_compat()</code> exist because Maya renamed these node types "
             "between versions. Use them instead of <code>cmds.createNode('addDoubleLinear')</code> "
             "if your rigs have to open in more than one Maya release.</p>"))

    # ---------------------------------------------------------- kinematics
    A(m.h2("FK, IK, twist, ribbons", "kinematics"))
    A("<p>The kinematics layer is where the time goes. These calls produce complete, working "
      "setups - controls, switches, stretch and all.</p>")
    A(m.table(["Call", "Produces"], [
        ["<code>mt.fk_chain(input, size, color, curve_type, scale, twist_axis, world_orient)</code>",
         "An FK control chain over selected joints"],
        ["<code>mt.simple_ik_chain(start, end, size, color, ik_curve, pv_curve, pv)</code>",
         "An IK handle with control and pole vector"],
        ["<code>mt.simple_fk_ik(start, mid, end, size, color, mode, twist_axis)</code>",
         "A three-joint FK/IK setup with a switch"],
        ["<code>mt.twist_fk_ik(start, mid, end, twist_amount=6, ...)</code>",
         "The same plus twist joints - a full limb"],
        ["<code>mt.streatchy_ik(ik, ik_ctrl, top_ctrl, pv_ctrl, attrs_location, axis)</code>",
         "Stretch nodes on an existing IK chain"],
        ["<code>mt.base_spline(start, end, size, name='Spine', amount=5)</code>",
         "An IK/FK spline spine"],
        ["<code>mt.advance_twist(start, end, axis, amount=4, mode='up', driver='')</code>",
         "Distributed twist joints reading real rotation"],
        ["<code>mt.spline_twist(start, end, axis, amount, mode, right_side)</code>",
         "Spline-driven twist"],
        ["<code>mt.basic_ribbon(start, end, divisions=5, ctrl_type='circleY')</code>",
         "A follicle ribbon with controls"],
        ["<code>mt.ribbon_between(start, end, divisions, ...)</code>",
         "A ribbon spanning two existing nodes"],
        ["<code>mt.curve_to_ribbon(curve, amount=5, direction='V')</code>",
         "A ribbon built along an existing curve"],
        ["<code>mt.pole_vector_placement(bone_one, bone_two, bone_three, back_distance)</code>",
         "The mathematically correct pole-vector position"],
        ["<code>mt.joints_middle(start, end, axis, amount=4, name='Twist')</code>",
         "Evenly spaced joints in a chain"],
        ["<code>mt.blend_between(ctrl, blends, attr_position, attr_name)</code>",
         "Space-switch blend groups and locators"],
        ["<code>mt.bend_and_squash(name, geo, parent_grp, squash_enabled, bend_enabled)</code>",
         "Squash and bend deformers with controls"],
        ["<code>mt.create_dynamic_fk(joints)</code>", "A dynamic FK chain"],
        ["<code>mt.dinamic_pivot(input, size)</code>", "A movable pivot rig on a control"],
        ["<code>mt.rivets_ctrls(geometry, selection_ctrls)</code>", "Controls stuck to geometry"],
    ]))
    A(m.note("<p>Most of these default their axis and shapes from <code>setup</code>, so calling "
             "<code>mt.fk_chain(input=joints)</code> with nothing else already matches the "
             "studio's house style. Only pass arguments you actually want to override.</p>"))

    # ----------------------------------------------------------- mirroring
    A(m.h2("Mirroring", "mirroring"))
    A("<p>Mirroring is a group-level trick, not a per-node one. <code>mt.mirror_group()</code> "
      "wraps a hierarchy in a group with a negative scale, so the whole branch flips at once and "
      "the maths stays exact.</p>")
    A("<p>Shipped blocks expose a <code>Mirror_enum</code> with three states and handle it "
      "<b>after</b> the controls exist:</p>")
    A(m.code("""
        mirror = cmds.getAttr('{}.Mirror'.format(config), asString=True)

        if mirror == 'Right_Only':
            clean_ctrl_grp = mt.mirror_group(clean_ctrl_grp, world=True)

        elif mirror == 'True':
            if side_guide.startswith(nc['right']):
                clean_ctrl_grp = mt.mirror_group(clean_ctrl_grp, world=True)
        """, "python"))
    A(m.table(["Value", "Meaning"], [
        ["<code>False</code>", "Build exactly what the guides describe"],
        ["<code>True</code>", "Build both sides, auto-prefixing <code>L_</code> where needed"],
        ["<code>Right_Only</code>", "Mirror the built result onto the right side only"],
    ]))
    A(m.warn("<p>Mirror <b>after</b> you create controls and <b>before</b> you rely on their world "
             "positions, and re-apply constraints afterwards. A constraint made before the mirror "
             "group is inserted will fight the negative scale.</p>"))

    # ---------------------------------------------------------- versioning
    A(m.h2("Block versioning", "versioning"))
    A("<p>This is not optional and it is the reason old rigs keep rebuilding. Implementation files "
      "carry a version; the launcher JSON does not.</p>")
    A(m.plain("""
        exec_mouth_v001.py        003_Mouth_v001.json      <- frozen, never edited again
        exec_mouth_v002.py        003_Mouth_v002.json      <- your new work
                                  003_Mouth.json           <- launcher, repointed to v002
        """, "naming"))
    A("<p>Shipping a new version:</p>")
    A("<ol>"
      "<li>Copy <code>exec_x_v001.py</code> and <code>NN_X_v001.json</code> to <code>_v002</code>.</li>"
      "<li>Make your changes <b>only</b> in the v002 files.</li>"
      "<li>Repoint the launcher JSON's <code>python_file</code>, <code>import</code>, "
      "<code>imp.reload</code>, <code>exec_command</code> and <code>build_command</code> at v002.</li>"
      "<li>Leave v001 on disk, untouched, forever.</li>"
      "</ol>")
    A(m.note("<p>A scene saved last year has <code>exec_mouth_v001.build_mouth_block()</code> "
             "baked into its config node's locked <code>Build_Command</code> string. If you "
             "deleted or rewrote v001, that scene no longer rebuilds. Keeping old versions is what "
             "makes the promise 'this rig can always be rebuilt' true.</p>"))

    A(m.h3("Adding an attribute to an existing block", "back-compat"))
    A("<p>Old config nodes in saved scenes will not have your new attribute. An unguarded "
      "<code>getAttr</code> is a hard error mid-build.</p>")
    A(m.code("""
        # WRONG - explodes on every scene saved before this attr existed
        independent_scale = cmds.getAttr('{}.IndependentScale'.format(config))

        # RIGHT - fall back to the JSON default
        independent_scale = (
            cmds.attributeQuery('IndependentScale', node=config, exists=True)
            and cmds.getAttr('{}.IndependentScale'.format(config))
        )
        """, "python"))

    # -------------------------------------------------------------- traps
    A(m.h2("Traps that will bite you", "traps"))
    A(m.cards([
        ("_float is an int, 1 to 20",
         "The JSON suffix lies. Add a real float with <code>mt.new_attr()</code> after "
         "<code>create_block</code> if you need one."),
        ("Type detection is a substring test",
         "<code>'string' in attr</code>, checked before enum, float and bool. Do not put a type "
         "word inside a descriptive attribute name."),
        ("root_grp invalidates DAG paths",
         "It reparents the node. Re-fetch the child from the returned group before you use it."),
        ("root_grp twice clashes",
         "Default suffixes collide. Pass <code>custom=True, custom_name='...'</code> for the second."),
        ("Build order is outliner order",
         "There is no dependency graph. If block B needs block A, A must sit above it."),
        ("Your build function takes no arguments",
         "It reads <code>cmds.ls(sl=True)</code>. The builder selects the block for you - guard "
         "for the empty case anyway."),
        ("New attrs break old scenes",
         "Always guard with <code>cmds.attributeQuery(..., exists=True)</code> and fall back to "
         "the JSON default."),
        ("Never delete an old block version",
         "Saved scenes hold the versioned call string in a locked attribute."),
        ("precode falls back to MEL",
         "If <code>exec</code> raises, the builder tries <code>mel.eval</code>. A Python syntax "
         "error can surface as a confusing MEL error."),
        ("Mutant() writes to the scene",
         "Constructing it creates a <code>Mutant_Tools</code> node. Expect it in clean-scene "
         "checks and asset publishes."),
    ], 2))

    # ------------------------------------------------------------ pipeline
    A(m.h2("Pipeline integration", "pipeline"))
    A(m.h3("Building without the UI", "headless"))
    A("<p>Nothing about a block needs the AutoRigger window. Call the same functions yourself and "
      "the same rig comes out - which is what makes batch rebuilds and CI checks possible.</p>")
    A(m.code("""
        from maya import cmds
        from Mutant_Tools.Utils.Rigging import main_mutant

        mt = main_mutant.Mutant()
        nc, curve_data, setup = mt.import_configs()

        cmds.file('/jobs/show/asset/rig_blocks.ma', open=True, force=True)

        blocks = cmds.listRelatives('Mutant_Build', children=True, type='transform') or []

        for block in blocks:
            name = block.replace(nc['module'], '')
            config = '{}_Config'.format(name)
            if not cmds.objExists(config):
                continue

            import_command = cmds.getAttr('{}.Import_Command'.format(config))
            build_command = cmds.getAttr('{}.Build_Command'.format(config))

            exec(import_command)
            cmds.select(block)
            eval(build_command)

        cmds.file(rename='/jobs/show/asset/rig_built.ma')
        cmds.file(save=True, type='mayaAscii')
        """, "batch rebuild"))
    A(m.warn("<p>Order matters and <code>listRelatives</code> gives you outliner order, which is "
             "what you want. Do not sort that list.</p>"))

    A(m.h3("Version and update checks", "versions"))
    A(m.code("""
        mt.get_local_version()          # from config/version.json
        mt.get_online_version()         # scrapes mutanttools.com/current_version/
        mt.get_github_latest_release()  # public GitHub API, no auth needed
        mt.check_for_updates(silent=False)
        mt.check_dev_mode()             # True while config/version.json has dev_mode on
        mt.toggle_dev_mode()
        """, "python"))
    A(m.note("<p>Turn <b>dev mode</b> on while you develop. It suppresses the update prompt, so "
             "your local edits are never overwritten by an auto-update mid-session.</p>"))

    A(m.h3("Reading and writing rig data", "io"))
    A(m.code("""
        mt.write_json(path, json_file, data)
        data = mt.read_json(path, json_file)
        """, "python"))
    A("<p>The <code>Utils/IO</code> package builds on this for skin weights "
      "(<code>NgSkin_Data</code>), control shapes (<code>Ctrl_Data</code>) and guide positions "
      "(<code>Guide_Data</code>) - which is how <code>009_Data/01_Load_Skin</code> and "
      "<code>02_Load_Ctrls</code> reapply data as ordinary blocks in the build order.</p>")

    # ------------------------------------------------------------------ ai
    A(m.h2("Using AI on this codebase", "ai"))
    A("<p>Mutant Tools ships machine-readable coding rules so an assistant writes blocks that "
      "match the house pattern instead of generic Maya Python. They live in the repo at "
      "<code>Docs/AI_MT_COMMAND_RULES.md</code> and "
      "<code>Docs/AI_MT_COMMAND_TUTORIAL.md</code>, and there is a "
      "<a href=\"/llms.txt\">llms.txt</a> at the site root.</p>")
    A("<p>Paste this at the start of a session:</p>")
    A(m.plain("""
        You are coding inside the Mutant_Tools Maya rigging workspace.

        Follow these rules strictly:
        1) Use the Mutant API entry point:
           from Mutant_Tools.Utils.Rigging import main_mutant
           mt = main_mutant.Mutant()
        2) In block functions, always import configs with:
           nc, curve_data, setup = mt.import_configs()
        3) In build functions, always validate base with:
           mt.check_is_there_is_base()
        4) Preserve existing block architecture and naming patterns
           (create_<block>_block / build_<block>_block).
        5) Before Maya operations, guard with cmds.objExists and
           cmds.attributeQuery(..., exists=True).
        6) If creating offset/root helper groups repeatedly, use
           mt.root_grp(input=node, custom=True, custom_name='UniqueSuffix')
           to avoid name clashes.
        7) If deleting/rebuilding constraints, cache constraint type + targets
           and restore deterministically with mo=True.
        8) Make minimal, focused edits only; do not refactor unrelated code.
        9) Use cmds.warning for recoverable issues and concise prints for success.
        10) Keep changes compatible with the existing Mutant_Tools style
            (the codebase mixes Python 2 and 3 patterns).
        11) When adding a new attribute to a block JSON, always guard its getAttr
            with cmds.attributeQuery(..., exists=True) so old saved rigs still build.
        12) Block versioning is required: create versioned exec/json files and keep
            the launcher JSON pointing at the active version.

        When requirements are ambiguous, choose the simplest solution consistent
        with existing blocks.
        """, "initial prompt"))
    A(m.note("<p>Add a scope line for narrow tasks: <i>&ldquo;Implement only the requested body "
             "section. Do not add leg/finger/spine logic.&rdquo;</i> Without it, assistants "
             "reliably over-build.</p>"))

    # ----------------------------------------------------------- reference
    A(m.h2("Where to go next", "reference"))
    A(m.cards([
        ("Command wiki", 'Every <code>mt</code> method with its full signature, plus all '
         '%d shipped blocks and their options. <a href="/wiki/">Open the wiki</a>' % stats["blocks"]),
        ("Source", 'The whole system is readable. <a href="https://github.com/RenderDeMartes/Mutant_Tools" '
         'target="_blank" rel="noopener">RenderDeMartes/Mutant_Tools</a>'),
        ("Auto rigger", 'What the blocks feel like from the artist side. '
         '<a href="/maya-auto-rigger/">Maya auto rigger</a>'),
        ("Learn", 'Workflow walkthroughs and production examples. <a href="/learn/">Learn</a>'),
        ("For riggers", 'The non-Python tour of the same system. <a href="/rigger/">Rigger guide</a>'),
        ("Free assets", 'Rigs and tools to pull apart. <a href="/free-assets/">Free assets</a>'),
    ], 3))

    A('<div class="mt-cta">'
      '<h2>Build something with it</h2>'
      '<p>Mutant Tools is free to download and the source is public. If you build a block worth '
      'sharing, or hit something this page did not answer, get in touch.</p>'
      '<a class="mt-btn" href="https://github.com/RenderDeMartes/Mutant_Tools" target="_blank" '
      'rel="noopener">Get Mutant Tools</a>'
      '<a class="mt-btn mt-btn--ghost" href="/contact/">Contact</a>'
      '</div>')

    A('<p class="mt-updated">Generated from <code>RenderDeMartes/Mutant_Tools</code> at '
      '<code>%s</code> &middot; %s</p>' % (stats["sha"], stats["date"]))

    A('</article></div></div>')
    A(m.TOC_JS)
    return "".join(b)
