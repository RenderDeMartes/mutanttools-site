# -*- coding: utf-8 -*-
"""/web-to-rig/: place a skeleton on a character in the browser, rig it in Maya.

The page is the frame for assets/js/joint-placer.js, which does all the work in
the browser with three.js. A model is read from the visitor's own disk and is
never uploaded or stored. three.js comes from jsDelivr through an import map,
pinned to one version so a release upstream cannot change the tool. Below the
tool, a walkthrough of what the download does in Maya, stage by stage, with
the WebToRig window in Mutant Tools (UI/WebToRig).
"""
import hashlib, io, os

import mt_md as m
import mt_shell as shell

THREE = "https://cdn.jsdelivr.net/npm/three@0.160.0/"
BVH = "https://cdn.jsdelivr.net/npm/three-mesh-bvh@0.7.8/build/index.module.js"
JS_PATH = os.path.join(shell.SITE, "assets", "js", "joint-placer.js")

TITLE = "Web to Rig - Free Online Auto Rigger for Maya | Mutant Tools"
DESC = ("Free online auto rigger for Maya: load an FBX, GLB or OBJ character, check the "
        "skeleton placed on it, and drop one file into Maya for a full Mutant Tools rig on "
        "Unreal's Manny skeleton. Runs in your browser; your model is never uploaded.")


def _js_src():
    # same cache-busting as the stylesheet: the URL changes when the file does
    digest = hashlib.sha1(io.open(JS_PATH, "rb").read()).hexdigest()[:10]
    return "/assets/js/joint-placer.js?v=%s" % digest


def _step(num, title, body, locked=True):
    lock = ' data-step-locked inert aria-disabled="true"' if locked else ""
    return ('<section class="mt-step"%s><p class="mt-kicker">%s</p><h2>%s</h2>%s</section>'
            % (lock, num, title, body))


# What happens after the download, in the order the user meets it.
NEXT = (
    ("folder-open", "01 &middot; Your computer", "Unzip the download",
     "One folder holds your character, Unreal&rsquo;s Manny skeleton fitted to it with its "
     "skin, the template guides and <code>Drag_into_Maya.py</code>. Keep them together."),
    ("cursor", "02 &middot; Maya", "Drop it on the viewport",
     "Drag <code>Drag_into_Maya.py</code> onto the viewport of Maya 2022 or newer. The Web to "
     "Rig window opens on that folder, one stage at a time."),
    ("download", "03 &middot; First time only", "Install Mutant Tools",
     "No Mutant Tools yet, or an older one? The first stage downloads the latest release from "
     "GitHub and installs it, with a progress bar, keeping any old copy as a backup."),
    ("add", "04 &middot; Stage 2", "Import the character",
     "Your character comes in standing as it did here, on the Manny skeleton, with the skin "
     "weights from this page. Any skeleton the file had is replaced."),
    ("eye", "05 &middot; Stage 3", "Place the template",
     "The HumanUnrealGameTemplate guides land on the joints you placed here, and the face "
     "guides follow the head. Check them, and move any you want, before building."),
    ("build", "06 &middot; Stage 4", "Build the rig",
     "Mutant Tools builds the body block by block, then the Manny joints follow it, so the "
     "skinned character moves with the controls."),
    ("capture", "07 &middot; Extra tab", "Test it with animation",
     "Key one of Mutant Tools&rsquo; Mixamo animations onto the rig and press play, then put "
     "it back in its bind pose."),
    ("edit", "08 &middot; Yours", "Edit and rebuild",
     "It is a normal Mutant Tools rig: change a guide or a block&rsquo;s settings and rebuild. "
     "For the face, pick its eyelid and lip edges, switch its blocks on and rebuild."),
)


def build(stats):
    pick = '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-pick>Choose a model</button>'
    demo = '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-demo>Try the example</button>'

    load = (
        '<p>Your file is opened right here in the browser. It is never uploaded and never '
        'saved.</p>'
        '<p class="mt-model">%s<span data-model-name>No model loaded</span></p>'
        '<div class="mt-row">%s%s</div>'
        '<div class="mt-note mt-error" data-error hidden role="alert">'
        '<b class="mt-tag">Could not load</b><p></p></div>'
        % (m.icon("folder"), pick, demo))

    body = (
        '<p>Everything is placed for you when the model loads. Drag a coloured marker or a '
        'white handle to correct it: a point carries what hangs below it (the neck takes the '
        'head, the shoulder the whole arm) and never what is above it. Elbows and knees move on '
        'their own, so the hands and feet stay put.</p>'
        '<ol class="mt-markers" data-marker-list></ol>'
        '<label class="mt-check"><input type="checkbox" data-mirror checked> Mirror left and right</label>'
        '<p class="mt-label">Model facing the wrong way?</p>'
        '<div class="mt-row">'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-turn>%s Turn 90&deg;</button>'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-upaxis aria-pressed="false">Z-up model</button>'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-reset>%s Auto place</button>'
        '</div>' % (m.icon("reload"), m.icon("build")))

    fingers = (
        '<p>Looking down on each hand, drag every finger&rsquo;s base (the knuckle) and its tip. '
        'The joints in between are spaced along the finger, and each finger stays flat in the '
        'plane it curls in.</p>'
        '<div class="mt-field"><label for="mt-fingers">Fingers per hand</label>'
        '<select id="mt-fingers" class="mt-select" data-fingers>'
        '<option value="5">5 &middot; thumb and four fingers</option>'
        '<option value="4">4 &middot; cartoon hand</option>'
        '<option value="3">3 &middot; thumb, index, middle</option>'
        '<option value="0">None &middot; a single hand joint</option></select></div>'
        '<ol class="mt-markers" data-finger-list></ol>'
        '<div class="mt-row">'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-go-view="top">%s Top view</button>'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-reset-fingers>%s Auto place fingers</button>'
        '</div>' % (m.icon("eye"), m.icon("build")))

    # clips from Quaternius' Universal Animation Library (CC0), in
    # assets/models/quaternius-animations.glb
    clips = [("", "None"), ("Idle_Loop", "Idle"), ("Walk_Loop", "Walk"), ("Jog_Fwd_Loop", "Jog"),
             ("Sprint_Loop", "Sprint"), ("Dance_Loop", "Dance"), ("Punch_Jab", "Jab"),
             ("Punch_Cross", "Cross punch"), ("Jump_Loop", "Jump"), ("Roll", "Roll"),
             ("Sword_Attack", "Sword attack"), ("Crouch_Fwd_Loop", "Crouch walk"),
             ("Sitting_Idle_Loop", "Sitting"), ("Swim_Fwd_Loop", "Swim"),
             ("Spell_Simple_Shoot", "Spell"), ("Death01", "Death")]
    options = "".join('<option value="%s">%s</option>' % c for c in clips)

    export = (
        '<p>Orbit round the skeleton in 3D and check every joint sits inside the mesh.</p>'
        '<div class="mt-row mt-row--gap">'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-go-view="3d">%s Check in 3D</button>'
        '</div>'
        '<div class="mt-field"><label for="mt-twists">Twist joints</label>'
        '<select id="mt-twists" class="mt-select" data-twists>'
        '<option value="2">2 per arm and leg bone</option>'
        '<option value="1">1 per arm and leg bone</option>'
        '<option value="0">None</option></select></div>'
        '<div class="mt-field"><label for="mt-scale">Scale</label>'
        '<select id="mt-scale" class="mt-select" data-scale>'
        '<option value="1">&times;1 &middot; keep the file&rsquo;s units</option>'
        '<option value="100">&times;100 &middot; metres to centimetres</option>'
        '<option value="0.01">&times;0.01 &middot; centimetres to metres</option></select></div>'
        '<div class="mt-field"><label for="mt-anim">Test the rig</label>'
        '<select id="mt-anim" class="mt-select" data-anim>%s</select></div>'
        '<p class="mt-meta"><span data-count></span>, named after the Mutant Tools human template '
        '(L_Elbow_Jnt).</p>'
        '<p class="mt-meta" data-skin-status aria-live="polite"></p>'
        '<div class="mt-stack">'
        '<button class="mt-btn" type="button" data-dl-zip>%s Download for Maya</button>'
        '<div class="mt-row">'
        '<button class="mt-btn mt-btn--ghost mt-btn--sm" type="button" data-dl-json>Skeleton only (.json)</button>'
        '</div></div>'
        '<p class="mt-meta mt-fine">The zip holds your character, Unreal&rsquo;s Manny skeleton fitted '
        'to it with its skin, the template guides and <code>Drag_into_Maya.py</code>. Drop that file on '
        'Maya&rsquo;s viewport and follow its stages: <a href="#next">what happens in Maya</a>.</p>'
        % (m.icon("build"), options, m.icon("download")))

    stage = (
        '<div class="mt-placer__stage" data-stage>'
        '<div class="mt-placer__canvas" data-canvas-host></div>'
        '<div class="mt-placer__layer" data-layer></div>'
        '<div class="mt-stage__bar">'
        '<div class="mt-seg" role="group" aria-label="View">'
        '<button type="button" data-view-btn="front" aria-pressed="true">Front</button>'
        '<button type="button" data-view-btn="side" aria-pressed="false">Side</button>'
        '<button type="button" data-view-btn="top" aria-pressed="false">Top</button>'
        '<button type="button" data-view-btn="3d" aria-pressed="false">3D</button></div>'
        '<div class="mt-seg mt-seg--hand" role="group" aria-label="Hand">'
        '<button type="button" data-hand-btn="r" aria-pressed="false">Right hand</button>'
        '<button type="button" data-hand-btn="l" aria-pressed="true">Left hand</button></div>'
        '<div class="mt-seg" role="group" aria-label="Display">'
        '<button type="button" data-xray aria-pressed="false">%s X-ray</button>'
        '<button type="button" data-bones aria-pressed="true">%s Skeleton</button>'
        '<button type="button" data-weights aria-pressed="false">Weights</button>'
        '<button type="button" data-topology aria-pressed="false">Topology</button></div>'
        '</div>'
        '<p class="mt-stage__hint" data-hint></p>'
        '<div class="mt-drop" data-dropzone>'
        '<span class="mt-card__icon">%s</span>'
        '<p class="mt-drop__title" data-drop-msg data-idle="Drop a GLB, FBX or OBJ here">'
        'Drop a GLB, FBX or OBJ here</p>'
        '<p class="mt-drop__sub">A character standing in a T or A pose, facing you. FBX keeps the '
        'vertex order Maya needs for skin weights.</p>'
        '<div class="mt-row mt-row--center">'
        '<button class="mt-btn" type="button" data-pick>Choose a model</button>%s</div>'
        '<noscript><p class="mt-drop__sub">Web to Rig needs JavaScript.</p></noscript>'
        '</div>'
        '<div class="mt-auto" data-auto hidden role="status" aria-live="polite">'
        '<span class="mt-card__icon">%s</span>'
        '<p class="mt-auto__title">Placing the skeleton</p>'
        '<ol class="mt-auto__steps" data-auto-steps></ol>'
        '<div class="mt-auto__track"><span data-auto-bar></span></div></div>'
        '<input type="file" accept=".glb,.gltf,.fbx,.obj" data-file hidden>'
        '</div>' % (m.icon("eye"), m.icon("build"), m.icon("folder-open"),
                    demo.replace("mt-btn--sm", ""), m.icon("build")))

    app = (
        '<div class="mt-placer" data-placer data-state="empty" data-view="front">'
        '<div class="mt-placer__intro">'
        '<p class="mt-kicker">Free tool &middot; runs in your browser</p>'
        '<h1>Web to Rig</h1>'
        '<p class="mt-lede">Place a skeleton on your character here, then drop one file into '
        'Maya for a full Mutant Tools rig, built on Unreal&rsquo;s Manny skeleton.</p></div>'
        + stage +
        '<div class="mt-placer__steps">'
        + _step("01 / Model", "Load your character", load, locked=False)
        + _step("02 / Body &middot; front view", "Place the body markers", body)
        + _step("03 / Fingers &middot; top view", "Place the fingers", fingers)
        + _step("04 / Check &middot; 3D view", "Check and download", export)
        + '</div></div>')

    how = []
    A = how.append
    A('<section class="mt-band" id="next"><div class="mt-wrap">')
    A('<div class="mt-split"><div><p class="mt-kicker">What&rsquo;s next</p>'
      '<h2>From the download to a full rig</h2></div>'
      '<div class="mt-body"><p>This page places the skeleton and works out the skin. Before '
      'downloading, try them: <b>Test the rig</b> plays an animation on your character with '
      'those weights, right here.</p>'
      '<p>Maya does the rest, in stages you can watch, each with its own progress bar. Nothing '
      'is built until you have checked the guides.</p></div></div>')
    A('<ol class="mt-grid mt-grid--4 mt-next">')
    for ico, kicker, title, text in NEXT:
        A('<li class="mt-card"><span class="mt-card__icon">%s</span><p class="mt-kicker">%s</p>'
          '<h3>%s</h3><p>%s</p></li>' % (m.icon(ico), kicker, title, text))
    A('</ol>')
    A('<p class="mt-meta mt-credit">The example character and the test animations are from '
      'Quaternius&rsquo; <a href="https://quaternius.com/packs/universalbasecharacters.html" '
      'target="_blank" rel="noopener">Universal Base Characters</a> and '
      '<a href="https://quaternius.itch.io/universal-animation-library" target="_blank" '
      'rel="noopener">Universal Animation Library</a>, released under CC0.</p>')
    A('<div class="mt-cta mt-cta--split"><div><h2>The rig is Mutant Tools</h2>'
      '<p>Blocks for the limbs, spine, face and the rest, rebuilt whenever you change a guide. '
      'Web to Rig is the quickest way in.</p></div>%s</div>'
      % m.actions(m.btn("See the auto rigger", "/maya-auto-rigger/"),
                  m.btn("Block catalogue", "/wiki/blocks/", ghost=True)))
    A('</div></section>')

    scripts = (
        '<script type="importmap">{"imports":{"three":"%sbuild/three.module.js",'
        '"three/addons/":"%sexamples/jsm/","three-mesh-bvh":"%s"}}</script>\n'
        '<script type="module" src="%s"></script>\n' % (THREE, THREE, BVH, _js_src()))

    return app + "".join(how) + scripts
