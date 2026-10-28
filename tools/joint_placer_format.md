# Web to Rig download

What `/web-to-rig/` downloads, for **WebToRig** in Mutant Tools
(`UI/WebToRig`), which imports the character on Unreal's Manny skeleton, places
the **HumanUnrealGameTemplate** guides and builds the rig. The page writes all
of it in `assets/js/joint-placer.js` (`bundle()`, `skeletonFile()`,
`mannyFile()`); bump the version there if a change would break a reader.

`<model>_mutant_tools.zip` holds one folder:

```
<model>_mutant_tools/
  Drag_into_Maya.py            drop on Maya's viewport (assets/maya/Drag_into_Maya.py)
  README.txt
  web_to_rig.json              which file is which (below)
  <model>.fbx                  the character, as loaded, unchanged
  manny_skeleton.json          Manny fitted to the character
  skeleton.json                the template guides and the placed joints
  skin/<model>.bSkinPack       Mutant Tools skin pack (IOSkin.importSkinPack)
  skin/<mesh>.jSkin            one per mesh, IOSkin's compressed jSkin format
```

"Skeleton only (.json)" downloads `skeleton.json` on its own.

## The frame

Every position in every file is in the page's frame: **Y up, the character
facing +Z**, as the front view shows it (after the page's own up-axis fix and
any 90-degree turns the user made), in centimetres (`units.scale` below).
Left (`L_`, `_l`) is the character's left: +X.

That is not always where Maya puts the file: its FBX import stands a model up
by all of the file's axis settings, and the page reads only the up axis. So
`web_to_rig.json` carries `anchors`, a few of each mesh's vertices with where
the page had them, and WebToRig fits the quarter turns, scale and offset that
put Maya's import there before anything is bound.

## web_to_rig.json

```json
{
  "format": "mutant-tools-web-to-rig",
  "version": 1,
  "model": "Superhero_Male",
  "mesh": "Superhero_Male.fbx",
  "meshes": ["Eyebrows", "Eyes", "SuperHero_Male"],
  "skeleton": "skeleton.json",
  "manny": "manny_skeleton.json",
  "skin_pack": "skin/Superhero_Male.bSkinPack",
  "template": "HumanUnrealGameTemplate",
  "units": "cm",
  "up_axis": "y",
  "fingers": 5,
  "anchors": { "SuperHero_Male": { "vertices": 6287, "points": [[1000, 8.7, 7.76, 5.06]] } },
  "site": "https://mutanttools.com/web-to-rig/"
}
```

| Field | Meaning |
|---|---|
| `mesh` | The character's own file in the folder. |
| `meshes` | The meshes that have a jSkin, by their model name in the file. |
| `skin_pack` | Null when the file's vertex order could not be read (no weights for Maya then). |
| `anchors` | Per mesh: its vertex count, and `[index, x, y, z]` for the extremes along each axis and about a dozen more, in the file's vertex numbering and the page's frame. |

## manny_skeleton.json

Unreal's Manny (`SKM_Manny_BaseSkeleton`, from Mutant Tools'
`Utils/Unreal/mannequin_skeleton_capture.json`) moved onto the character, in
the format `mannequin_utils.recreate_mannequin_from_json` reads: `joint_order`,
and per joint `parent`, `world_translate`, `world_rotate`, `local_translate`,
`local_rotate` (always zero), `joint_orient`, `rotate_order`, `radius`.
Positions come from the placed joints (twists at Manny's own fractions); each
joint keeps Manny's orientation, swung only as far as its bone now points
elsewhere, so Manny's axis conventions survive.

## skeleton.json

```json
{
  "format": "mutant-tools-skeleton",
  "version": 2,
  "template": "HumanUnrealGameTemplate",
  "source": { "tool": "Mutant Tools Web to Rig", "url": "https://mutanttools.com/web-to-rig/", "model": "Mannequin" },
  "units": { "scale": 100 },
  "upAxis": "y",
  "sourceUpAxis": "z",
  "fingers": 5,
  "guides": {
    "Spine_Root_Guide": [0, 95.09, 0],
    "L_Elbow_Guide": [49.99, 143.94, -1.09],
    "L_Foot_Heel_Guide": [10, 0, -6]
  },
  "joints": [
    { "key": "Spine_Root", "name": "Spine_Root_Jnt", "parent": null, "side": "C", "position": [0, 95.09, 0] },
    { "key": "Spine_Base", "name": "Spine_Base_Jnt", "parent": "Spine_Root_Jnt", "side": "C", "position": [0, 110.15, 0] }
  ],
  "markers": { "chin": [0, 154.0, 4.1], "L_Wrist": [73.9, 143.0, 0] }
}
```

| Field | Meaning |
|---|---|
| `units.scale` | The factor already applied to every position, to centimetres: the FBX's `UnitScaleFactor`, 100 for glTF (metres), 1 for OBJ, unless the user changed it. |
| `upAxis` | Always `y`. |
| `sourceUpAxis` | The model's own up axis: from the FBX's `GlobalSettings`, or `z` when the user flagged it or the model lies flatter than it stands. |
| `fingers` | 5, 4, 3 or 0. Decides which finger guides and joints exist. |
| `guides` | **What the template needs.** Template guide name -> position, for every body guide, both sides. Guides that share a spot in the template are written for each name (see below). Face guides are not placed: WebToRig moves them with the head and switches the face blocks off for the first build, since their eyelids and lips need edges picked on the mesh. |
| `joints` | The skeleton as joints, parents before children, named `<key>_Jnt`. |
| `markers` | The raw points the user placed. |

### Guides

Every guide below exists for `L_` and `R_`; the template itself only has the
`L_` side and mirrors it, so the `R_` values are there for asymmetric
characters and can be ignored.

| Guide | Placed from |
|---|---|
| `Spine_Root`, `Spine_Base`, `Spine_Belly`, `Spine_Chest` | The body's centre line, spaced as in the template between the root and the neck |
| `Spine_End`, `Neck` | The same point: the base of the neck |
| `Head`, `HeadEnd` | Just above the chin marker; the top of the mesh |
| `L_Clavicle` | Beside the neck at shoulder height |
| `L_ClavicleEnd`, `L_Shoulder` | The same point: the shoulder |
| `L_Elbow`, `L_Wrist` | The markers. The elbow is kept on the shoulder-wrist plane, bent back |
| `L_Hand_Palm` | The wrist |
| `L_Hand_InnerCup`, `L_Hand_OutterCup` | Between the wrist and the thumb / ring and pinky metacarpals |
| `L_Hand_Thumb_00` ... `_03` | Markers at `_00` (root by the wrist) and `_03` (tip); `_01`, `_02` spaced between |
| `L_Hand_<Index/Middle/Ring/Pinky>_00` ... `_04` | Markers at `_01` (knuckle) and `_04` (tip); `_02`, `_03` spaced between; `_00` between the wrist and the knuckle, on the plane the finger curls in (through knuckle and tip, square to the palm) |
| `L_Pelvis` | Above the hip |
| `L_PelvisEnd`, `L_Hip` | The same point: the hip joint |
| `L_Knee` | The marker, kept on the hip-ankle plane, bent forward |
| `L_Ankle`, `L_Foot_Ankle` | The same point: the middle of the shin above the foot |
| `L_Foot_Ball`, `L_Foot_Toes`, `L_Foot_Heel` | The foot's front and back from the mesh; toes and heel on the floor |
| `L_Foot_BallFloor`, `L_Foot_In`, `L_Foot_Out`, `L_Foot_HeelMid` | The ball dropped to the floor; the foot's inner and outer edge at the ball; a third of the way from heel to ball |

With `fingers` below 5 the missing fingers' guides are left out, and with 0
there are no finger or cup guides.

Every non-marker guide is the page's own placement plus whatever the user
dragged it by, so a guide can sit anywhere the user put it.

## Skin pack

Weights are worked out in the browser on the page's joints, then named for
the Manny joints they become (`MANNY_SKIN` in the page: the cups go to the
hand, the twist joints to Manny's twists, the rest by position):

- each vertex goes to the nearest bone it can see from inside its mesh (a
  ray from the bone must reach the vertex without leaving the surface); a mesh
  with no bone inside it, like an eyeball, takes the nearest bone;
- weights blend across each joint over the last fifth of a bone, are smoothed
  twice over the surface, and keep at most 4 joints per vertex, each at least
  0.01, normalised to 1.

Each `.jSkin` follows `IOSkin.exportSkin`'s compressed layout:
`{"objs": [name], "objDDic": [{"weights": {joint: {"<vertex>": w}}, "blendWeights": {},
"skinClsName": "<name>_skinCluster", "objName": name, "nameSpace": "", "vertexCount": n,
"skinDataFormat": "compressed", "skinningMethod": 0, "normalizeWeights": 1}], "bypassObj": []}`.
`objName` is the mesh's model name in the FBX. Maya may rename a mesh on import
(`Body.001` comes in as `BodyFBXASC046001`); WebToRig matches it back by name
or vertex count.

Vertex indices are the **file's own order**, which is what Maya keeps: an FBX's
control points (read straight from the binary FBX, not from three.js), or an
OBJ's `v` lines. So the pack only applies to the same file the weights were made
on. Files where that order cannot be known get weights for the on-screen
preview only and no pack: GLB (Maya cannot import it), text FBX, and OBJ files
with more than one object.

## How positions are made

Front-view markers sit halfway between the front-most and back-most surface a
ray through the mesh crosses; top-view markers halfway through the slab a ray
from above meets.
