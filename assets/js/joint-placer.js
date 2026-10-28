// Web to Rig: Mutant Tools' joint placer.
//
// Load a character and place the Mutant Tools human template on it in three
// passes, the way a rigger would: the body's key points in the front view,
// each finger from above, then a look round in 3D before downloading. Every
// joint is pushed to the middle of the mesh: front-view points by a ray through
// the body, top-view points by a ray down through the hand.
//
// The skeleton follows the guides of Mutant Tools' HumanUnrealGameTemplate
// (Spine_Root ... HeadEnd, L_Clavicle ... L_Hand_Pinky_04, L_Pelvis ...
// L_Foot_Toes). Eight markers drive it; every other joint is placed from them
// and the mesh, and can then be dragged as a handle, which stores an offset so
// it keeps following when the markers move. Elbows and knees always stay on
// their limb's bend plane, with a slight bend, so IK has a direction to solve;
// each finger stays on the plane it curls in.
//
// The download is a folder for Maya (format: tools/joint_placer_format.md):
// the character, Unreal's Manny skeleton fitted to it with its skin, the
// template guides, and Drag_into_Maya.py, which builds the rig from them.
//
// Everything runs in the browser. The model is read from the visitor's disk,
// never uploaded and never stored, and the loaders are stopped from fetching
// the textures a model names, so not even a file name reaches the server.

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { unzlibSync, zipSync, strToU8 } from 'three/addons/libs/fflate.module.js';
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';

// Every ray (depth, height, and the thousands the skin weights need) goes
// through a BVH instead of testing each triangle.
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;
THREE.SkinnedMesh.prototype.raycast = acceleratedRaycast;

const EXAMPLE = { url: '/assets/models/Superhero_Male_FullBody.fbx', name: 'Superhero_Male_FullBody.fbx' };
const FORMAT = 'mutant-tools-skeleton';
const FORMAT_VERSION = 2;
const TEMPLATE = 'HumanUnrealGameTemplate';

const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), hi);
const SIDES = ['L_', 'R_'];
const SIDE_LABEL = { L_: 'Left', R_: 'Right' };
const SIGN = { L_: 1, R_: -1 };
const sideOf = (id) => (id.startsWith('L_') ? 'L_' : id.startsWith('R_') ? 'R_' : '');
const twinOf = (id) => (sideOf(id) ? (sideOf(id) === 'L_' ? 'R_' : 'L_') + id.slice(2) : null);
const cap = (s) => s[0].toUpperCase() + s.slice(1);

// Each limb bends toward its pole: elbows back, knees forward.
const ELBOW_POLE = V(0, 0, -1);
const KNEE_POLE = V(0, 0, 1);
const MIN_BEND = 0.02; // of the limb's length

const FINGERS = [
  { id: 'thumb', label: 'Thumb', color: '#F0B3DE', joints: ['00', '01', '02', '03'] },
  { id: 'index', label: 'Index', color: '#D8A47F', joints: ['00', '01', '02', '03', '04'] },
  { id: 'middle', label: 'Middle', color: '#5AB1BB', joints: ['00', '01', '02', '03', '04'] },
  { id: 'ring', label: 'Ring', color: '#7DD181', joints: ['00', '01', '02', '03', '04'] },
  { id: 'pinky', label: 'Pinky', color: '#A96DA3', joints: ['00', '01', '02', '03', '04'] },
];
const FINGER = Object.fromEntries(FINGERS.map((f) => [f.id, f]));
const FINGER_SETS = {
  5: ['thumb', 'index', 'middle', 'ring', 'pinky'],
  4: ['thumb', 'index', 'middle', 'ring'],
  3: ['thumb', 'index', 'middle'],
  0: [],
};
// The two markers per finger, and where its other joints sit between them.
// The thumb is placed from its root by the wrist; the others from the knuckle.
const fingerKey = (P, f, n) => P + 'Hand_' + cap(f) + '_' + n;
const FINGER_ENDS = { thumb: ['00', '03'], other: ['01', '04'] };
const FINGER_STEPS = { thumb: { '01': 0.22, '02': 0.61 }, other: { '02': 0.4, '03': 0.72 } };

// Draggable points. Markers are placed directly; handles are joints the page
// places itself, nudged by an offset. `front` / `top` say what a drag in that
// view does with the third axis: find the middle of the mesh, or keep it.
const POINTS = [
  { id: 'chin', label: 'Chin', color: '#FF6B6B', kind: 'marker', views: 'front side', front: 'center' },
  { id: 'groin', label: 'Groin', color: '#FFE66D', kind: 'marker', views: 'front side', front: 'center' },
];
const BODY_MARKERS = ['chin', 'groin'];
for (const P of SIDES) {
  const side = SIDE_LABEL[P];
  POINTS.push(
    { id: P + 'Elbow', label: side + ' elbow', color: '#4ECDC4', kind: 'marker', views: 'front side top', front: 'center', top: 'height' },
    { id: P + 'Wrist', label: side + ' wrist', color: '#BFD7EA', kind: 'marker', views: 'front side top', front: 'center', top: 'height' },
    { id: P + 'Knee', label: side + ' knee', color: '#91AEC1', kind: 'marker', views: 'front side', front: 'center' },
  );
  BODY_MARKERS.push(P + 'Wrist', P + 'Elbow', P + 'Knee');
  for (const f of FINGERS) {
    const [a, b] = FINGER_ENDS[f.id === 'thumb' ? 'thumb' : 'other'];
    POINTS.push(
      { id: fingerKey(P, f.id, a), label: side + ' ' + f.id + ' base', color: f.color, kind: 'marker', views: 'top', top: 'height', finger: f.id },
      { id: fingerKey(P, f.id, b), label: side + ' ' + f.id + ' tip', color: f.color, kind: 'marker', views: 'top', top: 'height', finger: f.id, tip: true },
    );
  }
}
const HANDLE = (id, label, views, front = 'center', top = 'keep', extra = {}) =>
  POINTS.push({ id, label, color: '#F2EFE8', kind: 'handle', views, front, top, ...extra });
HANDLE('Spine_Root', 'Spine root', 'front side');
HANDLE('Spine_Base', 'Spine base', 'front side');
HANDLE('Spine_Belly', 'Belly', 'front side');
HANDLE('Spine_Chest', 'Chest', 'front side');
HANDLE('Neck', 'Neck', 'front side');
HANDLE('Head', 'Head', 'front side');
HANDLE('HeadEnd', 'Head top', 'front side', 'keep');
for (const P of SIDES) {
  const side = SIDE_LABEL[P];
  HANDLE(P + 'Eyes', side + ' eye', 'front side', 'keep');
  HANDLE(P + 'Clavicle', side + ' clavicle', 'front side', 'keep');
  HANDLE(P + 'Shoulder', side + ' shoulder', 'front side top');
  HANDLE(P + 'Pelvis', side + ' pelvis', 'front side');
  HANDLE(P + 'Hip', side + ' hip', 'front side');
  HANDLE(P + 'Ankle', side + ' ankle', 'front side', 'keep');
  HANDLE(P + 'Foot_Ball', side + ' ball', 'side', 'keep');
  HANDLE(P + 'Foot_Toes', side + ' toes', 'side', 'keep');
  HANDLE(P + 'Foot_Heel', side + ' heel', 'side', 'keep');
  // the pivots the foot rocks on, on the floor across from the ball
  HANDLE(P + 'Foot_In', side + ' foot inside', 'front', 'keep');
  HANDLE(P + 'Foot_Out', side + ' foot outside', 'front', 'keep');
  HANDLE(P + 'Hand_InnerCup', side + ' inner cup', 'top', 'keep', 'height', { finger: 'thumb' });
  HANDLE(P + 'Hand_OutterCup', side + ' outer cup', 'top', 'keep', 'height', { finger: 'ring pinky' });
  for (const f of FINGERS) {
    if (f.id !== 'thumb') HANDLE(fingerKey(P, f.id, '00'), side + ' ' + f.id + ' 00', 'top', 'keep', 'height', { finger: f.id });
    for (const n in FINGER_STEPS[f.id === 'thumb' ? 'thumb' : 'other']) {
      HANDLE(fingerKey(P, f.id, n), side + ' ' + f.id + ' ' + n, 'top', 'keep', 'height', { finger: f.id, middle: true });
    }
  }
}
const POINT = Object.fromEntries(POINTS.map((p) => [p.id, p]));

// Twist joints, like the Unreal mannequin's: on each long bone, parented to
// the joint the bone starts from and spaced evenly along it.
const TWIST_BONES = [['Shoulder', 'Elbow'], ['Elbow', 'Wrist'], ['Hip', 'Knee'], ['Knee', 'Ankle']];
const twistKey = (P, from, i) => P + from + '_Twist_0' + i;
const isTwist = (key) => /_Twist_\d+$/.test(key);

// The skeleton, parents first, for a finger count and twists per bone. Keys
// are the template's guide names without "_Guide"; joints are key + "_Jnt".
function jointList(count, twists = 0) {
  const fingers = FINGER_SETS[count];
  const list = [
    ['Spine_Root', null], ['Spine_Base', 'Spine_Root'], ['Spine_Belly', 'Spine_Base'],
    ['Spine_Chest', 'Spine_Belly'], ['Neck', 'Spine_Chest'], ['Head', 'Neck'], ['HeadEnd', 'Head'],
  ];
  const chain = (P, f, parent) => {
    for (const n of FINGER[f].joints) {
      list.push([fingerKey(P, f, n), parent]);
      parent = fingerKey(P, f, n);
    }
  };
  for (const P of SIDES) {
    list.push([P + 'Clavicle', 'Spine_Chest'], [P + 'Shoulder', P + 'Clavicle'],
      [P + 'Elbow', P + 'Shoulder'], [P + 'Wrist', P + 'Elbow']);
    if (!fingers.length) list.push([P + 'Hand_End', P + 'Wrist']);
    if (fingers.includes('thumb')) {
      list.push([P + 'Hand_InnerCup', P + 'Wrist']);
      chain(P, 'thumb', P + 'Hand_InnerCup');
    }
    for (const f of ['index', 'middle']) if (fingers.includes(f)) chain(P, f, P + 'Wrist');
    const outer = ['ring', 'pinky'].filter((f) => fingers.includes(f));
    if (outer.length) {
      list.push([P + 'Hand_OutterCup', P + 'Wrist']);
      for (const f of outer) chain(P, f, P + 'Hand_OutterCup');
    }
    list.push([P + 'Pelvis', 'Spine_Root'], [P + 'Hip', P + 'Pelvis'], [P + 'Knee', P + 'Hip'],
      [P + 'Ankle', P + 'Knee'], [P + 'Foot_Ball', P + 'Ankle'], [P + 'Foot_Toes', P + 'Foot_Ball']);
    for (const [from] of TWIST_BONES) {
      for (let i = 1; i <= twists; i++) list.push([twistKey(P, from, i), P + from]);
    }
  }
  return list;
}
const ALL_KEYS = [...new Set([...jointList(5, 2), ...jointList(0)].map(([k]) => k))];

// The spine's inner joints, spaced as in the template between the root and the
// neck. They re-space when either end moves.
const SPINE = [['Spine_Base', 0.274], ['Spine_Belly', 0.518], ['Spine_Chest', 0.723]];
const SPINE_KEYS = new Set(SPINE.map(([k]) => k));

// What carries what while placing: moving a point moves everything under it
// here and nothing above it. The neck takes the chin, head and eyes along;
// the chest takes the clavicles and arms; the groin takes the root and legs.
// The wrist and ankle hang off the shoulder and hip, so a bend can be fixed at
// the elbow or knee without moving the hand or the foot. A finger's middle
// joints are not here: they keep their place between its markers.
const PLACE_PARENT = { Spine_Root: 'groin', chin: 'Neck', Head: 'chin', HeadEnd: 'Head' };
for (const P of SIDES) {
  Object.assign(PLACE_PARENT, {
    [P + 'Clavicle']: 'Spine_Chest', [P + 'Shoulder']: P + 'Clavicle', [P + 'Elbow']: P + 'Shoulder',
    [P + 'Wrist']: P + 'Shoulder', [P + 'Hand_InnerCup']: P + 'Wrist', [P + 'Hand_OutterCup']: P + 'Wrist',
    [P + 'Pelvis']: 'Spine_Root', [P + 'Hip']: P + 'Pelvis', [P + 'Knee']: P + 'Hip', [P + 'Ankle']: P + 'Hip',
    [P + 'Foot_Ball']: P + 'Ankle', [P + 'Foot_Toes']: P + 'Foot_Ball', [P + 'Foot_Heel']: P + 'Ankle',
    [P + 'Foot_In']: P + 'Ankle', [P + 'Foot_Out']: P + 'Ankle', [P + 'Eyes']: 'Head',
    [fingerKey(P, 'thumb', '00')]: P + 'Hand_InnerCup', [fingerKey(P, 'thumb', '03')]: fingerKey(P, 'thumb', '00'),
  });
  for (const f of ['index', 'middle', 'ring', 'pinky']) {
    PLACE_PARENT[fingerKey(P, f, '00')] = f === 'ring' || f === 'pinky' ? P + 'Hand_OutterCup' : P + 'Wrist';
    PLACE_PARENT[fingerKey(P, f, '01')] = fingerKey(P, f, '00');
    PLACE_PARENT[fingerKey(P, f, '04')] = fingerKey(P, f, '01');
  }
}
const PLACE_CHILDREN = {};
for (const [k, p] of Object.entries(PLACE_PARENT)) (PLACE_CHILDREN[p] || (PLACE_CHILDREN[p] = [])).push(k);

// Template guides that are not joints of their own: where each one sits.
const GUIDE_ALIASES = { Spine_End: 'Neck', ClavicleEnd: 'Shoulder', PelvisEnd: 'Hip', Foot_Ankle: 'Ankle', Hand_Palm: 'Wrist' };
const FOOT_GUIDES = ['Foot_Heel', 'Foot_HeelMid', 'Foot_BallFloor', 'Foot_In', 'Foot_Out'];
// How far ahead of the eye its aim guide sits, of the body's height: about
// where the template has it.
const EYE_AIM = 0.2;

const HINTS = {
  front: 'Front: drag the coloured markers onto the joints; white handles fine-tune the rest. Scroll to zoom.',
  side: 'Side: drag forward or back to fix depth, and set the ankle, ball, toes and heel. Scroll to zoom.',
  top: 'Top: place each finger’s base and tip, slide the joints between onto the creases, and fix the elbow’s bend. Scroll to zoom.',
  '3d': 'Drag to orbit, scroll to zoom. Check the joints sit inside the mesh.',
};

const root = document.querySelector('[data-placer]');
if (root) init(root);

function init(root) {
  const $ = (sel) => root.querySelector(sel);
  const $$ = (sel) => [...root.querySelectorAll(sel)];
  const stage = $('[data-stage]');
  const layer = $('[data-layer]');
  const dropMsg = $('[data-drop-msg]');
  const errorBox = $('[data-error]');

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch (err) {
    dropMsg.textContent = 'This browser cannot show 3D (WebGL is off or unsupported).';
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x1a1a1e);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  $('[data-canvas-host]').append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x2e2e34, 2.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5);
  sun.position.set(1, 2, 3);
  scene.add(sun);

  const ortho = new THREE.OrthographicCamera();
  const persp = new THREE.PerspectiveCamera(35, 1, 0.01, 1000);
  const controls = new OrbitControls(persp, renderer.domElement);
  controls.enabled = false;
  controls.addEventListener('change', invalidate);

  // One clay material for every mesh: textures would only fight the markers.
  const clay = new THREE.MeshStandardMaterial({
    color: 0x9a968c, roughness: 0.85, metalness: 0, side: THREE.DoubleSide, transparent: true,
  });

  // The skeleton, drawn on top of the mesh. Buffers are sized for the most
  // joints any finger count needs; the draw range trims the rest.
  const bonesMat = new THREE.LineBasicMaterial({ color: 0xffe66d, depthTest: false, transparent: true });
  const jointMat = new THREE.MeshBasicMaterial({ color: 0xffe66d, depthTest: false, transparent: true });
  const bones = new THREE.LineSegments(new THREE.BufferGeometry(), bonesMat);
  bones.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(ALL_KEYS.length * 6), 3));
  bones.renderOrder = 10;
  bones.frustumCulled = false;
  const skeleton = new THREE.Group();
  skeleton.add(bones);
  const balls = {};
  const ballGeo = new THREE.SphereGeometry(1, 12, 8);
  for (const key of ALL_KEYS) {
    balls[key] = new THREE.Mesh(ballGeo, jointMat);
    balls[key].renderOrder = 11;
    skeleton.add(balls[key]);
  }
  // the eyes and the foot's rock pivots are guides, not joints: dots, no bones
  const pivotMat = new THREE.MeshBasicMaterial({ color: 0xf2efe8, depthTest: false, transparent: true });
  const PIVOTS = SIDES.flatMap((P) => [P + 'Eyes', P + 'Foot_In', P + 'Foot_Out']);
  for (const key of PIVOTS) {
    balls[key] = new THREE.Mesh(ballGeo, pivotMat);
    balls[key].renderOrder = 11;
    skeleton.add(balls[key]);
  }
  skeleton.visible = false;
  scene.add(skeleton);

  const S = {
    pivot: null, meshes: [], bounds: new THREE.Box3(), H: 1, cx: 0,
    points: new Float32Array(0), profile: [], feet: [], ankleX: {},
    pos: {}, spineOff: {}, mids: {}, eyeParts: new Set(), joints: {}, list: jointList(5, 2), fingers: 5, twists: 2, hand: 'L_',
    view: 'front', up: 'y', turn: 0, name: 'model', selected: null,
  };
  const ray = new THREE.Raycaster();
  const BACK = V(0, 0, -1);
  const DOWN = V(0, -1, 0);

  // ------------------------------------------------------------ rendering
  let frame = 0;
  function invalidate() {
    if (!frame) frame = requestAnimationFrame(draw);
  }
  function draw() {
    frame = 0;
    renderer.render(scene, S.view === '3d' ? persp : ortho);
    placePoints();
  }
  function size() {
    return { w: stage.clientWidth, h: stage.clientHeight };
  }
  new ResizeObserver(() => {
    const { w, h } = size();
    if (!w || !h) return;
    renderer.setSize(w, h);
    fitView(false);
    invalidate();
  }).observe(stage);

  function fitView(resetOrbit) {
    const { w, h } = size();
    if (!w || !h || !S.pivot) return;
    const b = S.bounds, c = b.getCenter(V()), sz = b.getSize(V()), aspect = w / h;
    if (S.view === '3d') {
      persp.aspect = aspect;
      persp.near = S.H / 100;
      persp.far = S.H * 50;
      persp.updateProjectionMatrix();
      if (resetOrbit) {
        persp.position.set(c.x + S.H * 0.9, c.y + S.H * 0.3, c.z + S.H * 2.4);
        controls.target.copy(c);
        controls.update();
      }
      return;
    }
    let fh, target = c;
    const d = S.H * 4 + Math.max(sz.x, sz.z);
    if (S.view === 'top') {
      // frame one forearm and hand, from the elbow out past the fingertips;
      // the wheel zooms out to the shoulder
      const from = S.pos[S.hand + 'Elbow'];
      if (!from) return;
      const reach = handReach(S.hand);
      target = from.clone().lerp(reach.tip, 0.5);
      const span = Math.max(from.distanceTo(reach.tip) * 1.25, S.H * 0.12);
      fh = aspect < 1 ? span / aspect : span;
      ortho.position.set(target.x, b.max.y + d, target.z);
      ortho.up.set(0, 0, -1);
    } else {
      const across = S.view === 'front' ? sz.x : sz.z;
      fh = Math.max(S.H, across / aspect) * 1.15;
      if (S.view === 'front') ortho.position.set(c.x, c.y, c.z + d);
      else ortho.position.set(c.x + d, c.y, c.z);
      ortho.up.set(0, 1, 0);
    }
    ortho.left = -fh * aspect / 2; ortho.right = fh * aspect / 2;
    ortho.top = fh / 2; ortho.bottom = -fh / 2;
    ortho.zoom = 1;
    ortho.near = 0;
    ortho.far = d * 2 + S.H;
    ortho.lookAt(target);
    ortho.updateProjectionMatrix();
    ortho.updateMatrixWorld();
  }

  // ------------------------------------------------------------- loading
  // Textures and other files a model points at resolve to a blank pixel: the
  // model is drawn in clay anyway, and nothing about it should reach a server.
  const BLANK = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEAAAAALAAAAAABAAEAAAIBAAA=';
  const manager = new THREE.LoadingManager();
  manager.setURLModifier((url) => (/^(blob|data):/.test(url) ? url : BLANK));

  async function loadFile(file) {
    if (!file) return;
    showError('');
    busy('Reading ' + file.name + '…');
    try {
      await loadBuffer(file.name, await file.arrayBuffer());
    } catch (err) {
      console.error(err);
      busy('');
      showError('That file could not be read. Use a GLB, FBX or OBJ with the mesh in it ' +
        '(a .gltf with a separate .bin will not load; export it as GLB).');
    }
  }

  async function loadExample() {
    showError('');
    busy('Loading the example character…');
    try {
      const res = await fetch(EXAMPLE.url);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      await loadBuffer(EXAMPLE.name, await res.arrayBuffer());
    } catch (err) {
      console.error(err);
      busy('');
      showError('The example character did not load. Try again, or open your own model.');
    }
  }

  // Parse a model, and keep its vertex order as Maya will see it: a skin file
  // addresses vertices by index, so the weights must follow the file's own
  // order (FBX control points, OBJ "v" lines), not three.js's.
  async function loadBuffer(fileName, buffer) {
    const ext = fileName.split('.').pop().toLowerCase();
    // the file itself goes into the download, unchanged, for Maya to import
    S.source = { name: fileName, bytes: new Uint8Array(buffer.slice(0)) };
    let object, scale = 1, order = null, note = '', up = null;
    if (ext === 'glb' || ext === 'gltf') {
      const gltf = await new Promise((ok, fail) => new GLTFLoader(manager).parse(buffer, '', ok, fail));
      object = gltf.scene;
      scale = 100; // glTF is in metres, Maya in centimetres
      note = 'Maya cannot open GLB, so skin weights are a preview only. Load the FBX or OBJ ' +
        'the character came from to export them.';
    } else if (ext === 'fbx') {
      object = new FBXLoader(manager).parse(buffer, '');
      const fbx = readFbxMeshes(buffer);
      if (fbx) {
        order = fbx.meshes;
        // stand a Z-up file upright and convert its units, as Maya does
        scale = fbx.unitScale;
        up = fbx.upAxis === 2 ? 'z' : 'y';
      } else {
        note = 'This is a text FBX; save it as binary FBX to export skin weights.';
      }
    } else if (ext === 'obj') {
      const text = new TextDecoder().decode(buffer);
      object = new OBJLoader(manager).parse(text);
      const obj = readObjVertices(text, fileName);
      if (obj.objects > 1) note = 'This OBJ holds several objects; export it as FBX to get skin weights for each.';
      else order = [obj];
    } else {
      throw new Error('Unsupported file type .' + ext);
    }
    setModel(object, fileName, scale, order, note, up);
  }

  function setModel(object, fileName, scale, order = null, note = '', up = null) {
    stopTest(true);
    const extras = [];
    const meshes = [];
    object.traverse((o) => {
      if (o.isLight || o.isCamera) extras.push(o);
      if (o.isMesh) {
        if (o.geometry.index) o.geometry = o.geometry.toNonIndexed();
        o.material = clay;
        o.frustumCulled = false;
        meshes.push(o);
      }
    });
    if (!meshes.length) throw new Error('No mesh in file');
    extras.forEach((o) => o.removeFromParent());
    meshes.forEach((m) => m.geometry.computeBoundsTree());

    if (S.pivot) {
      scene.remove(S.pivot);
      S.pivot.traverse((o) => {
        if (!o.geometry) return;
        if (o.geometry.boundsTree) o.geometry.disposeBoundsTree();
        o.geometry.dispose();
      });
    }
    S.pivot = new THREE.Group();
    S.pivot.add(object);
    scene.add(S.pivot);
    S.meshes = meshes;
    S.order = order;
    S.skinNote = note;
    S.weights = null;
    showWeights(false);
    S.name = fileName.replace(/\.[^.]+$/, '') || 'model';
    // a model with no say in the matter is Z-up when it lies flatter than it stands
    if (!up) {
      const sz = new THREE.Box3().setFromObject(object, true).getSize(V());
      up = sz.y < 0.5 * Math.max(sz.x, sz.z) ? 'z' : 'y';
    }
    S.up = up;
    S.turn = 0;
    setScale(scale);
    $('[data-upaxis]').setAttribute('aria-pressed', String(up === 'z'));
    $('[data-model-name]').textContent = fileName;

    root.dataset.state = 'ready';
    $$('[data-step-locked]').forEach((el) => { el.inert = false; el.removeAttribute('aria-disabled'); });
    busy('');
    skeleton.visible = $('[data-bones]').getAttribute('aria-pressed') === 'true';
    orient();
  }

  // Up axis and facing are a rotation of the pivot. Exports undo it, so the
  // joints come out in the file's own space and line up with it in Maya.
  function orient() {
    S.pivot.rotation.set(S.up === 'z' ? -Math.PI / 2 : 0, S.turn * Math.PI / 2, 0, 'YXZ');
    S.pivot.updateMatrixWorld(true);
    measure();
    fitView(true);
    autoPlace();
  }

  // ------------------------------------------------------------ the mesh
  function measure() {
    S.bounds.setFromObject(S.pivot, true);
    const b = S.bounds;
    S.H = b.max.y - b.min.y || 1;
    S.cx = (b.min.x + b.max.x) / 2;
    S.points = samplePoints(60000);
    for (const key in balls) balls[key].scale.setScalar(S.H * 0.005);

    // the front and back of the body's centre line, once per model: the
    // spine, neck and head take their depth from here
    const n = 128, raw = [];
    for (let i = 0; i <= n; i++) raw.push(rayZ(S.cx, b.min.y + S.H * i / n));
    const nearest = (i) => {
      if (raw[i]) return raw[i];
      for (let d = 1; d <= n; d++) {
        if (raw[i - d]) return raw[i - d];
        if (raw[i + d]) return raw[i + d];
      }
      return { front: b.max.z, back: b.min.z };
    };
    S.zLine = raw.map((_, i) => nearest(i));
    S.profile = S.zLine.map((z) => (z.front + z.back) / 2);

    // points near the floor, for the toes, heel and foot sides
    S.feet = [];
    const P = S.points, top = b.min.y + S.H * 0.07;
    for (let i = 0; i < P.length; i += 3) if (P[i + 1] < top) S.feet.push(P[i], P[i + 1], P[i + 2]);

    // each ankle sits in the middle of its shin, just above the foot
    for (const s of SIDES) S.ankleX[s] = sliceMid(b.min.y + S.H * 0.09, SIGN[s], 0.25);
  }

  // Points over the whole surface, about `max` of them, spread by area: a
  // low-poly model's vertices alone leave thin slices of it nearly empty.
  function samplePoints(max) {
    const tris = [];
    let area = 0;
    const a = V(), b = V(), c = V(), e1 = V(), e2 = V();
    for (const m of S.meshes) {
      const pos = m.geometry.attributes.position, index = m.geometry.index;
      const world = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) m.getVertexPosition(i, a).applyMatrix4(m.matrixWorld).toArray(world, i * 3);
      const n = index ? index.count / 3 : pos.count / 3;
      for (let t = 0; t < n; t++) {
        const i0 = index ? index.getX(t * 3) : t * 3, i1 = index ? index.getX(t * 3 + 1) : t * 3 + 1;
        const i2 = index ? index.getX(t * 3 + 2) : t * 3 + 2;
        a.fromArray(world, i0 * 3); b.fromArray(world, i1 * 3); c.fromArray(world, i2 * 3);
        const s = e1.subVectors(b, a).cross(e2.subVectors(c, a)).length() / 2;
        area += s;
        tris.push(world, i0, i1, i2, s);
      }
    }
    const out = [];
    let carry = 0, seed = 1;
    // a fixed sequence, so the same model always lands the same way
    const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let k = 0; k < tris.length; k += 5) {
      const [world, i0, i1, i2, s] = tris.slice(k, k + 5);
      // every corner once, plus inner points in proportion to the area
      carry += (s / (area || 1)) * max;
      let count = Math.floor(carry);
      carry -= count;
      a.fromArray(world, i0 * 3); b.fromArray(world, i1 * 3); c.fromArray(world, i2 * 3);
      out.push(a.x, a.y, a.z);
      for (; count > 0; count--) {
        let u = rand(), w = rand();
        if (u + w > 1) { u = 1 - u; w = 1 - w; }
        out.push(a.x + (b.x - a.x) * u + (c.x - a.x) * w, a.y + (b.y - a.y) * u + (c.y - a.y) * w,
          a.z + (b.z - a.z) * u + (c.z - a.z) * w);
      }
    }
    return new Float32Array(out);
  }

  // The middle, across X, of one side's slice of the mesh at height y: how the
  // knees and ankles are found. Null when that side has nothing there.
  function sliceMid(y, sign, reach) {
    const P = S.points, band = S.H * 0.015;
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < P.length; i += 3) {
      const out = (P[i] - S.cx) * sign;
      if (out > 0 && out < reach * S.H && Math.abs(P[i + 1] - y) < band) {
        lo = Math.min(lo, P[i]);
        hi = Math.max(hi, P[i]);
      }
    }
    return lo < hi ? (lo + hi) / 2 : null;
  }

  // Where a ray from the front at (x, y) first enters the body and finally
  // leaves it, or null when it misses.
  function rayZ(x, y) {
    ray.set(V(x, y, S.bounds.max.z + S.H), BACK);
    const hits = ray.intersectObjects(S.meshes, false);
    return hits.length ? { front: hits[0].point.z, back: hits[hits.length - 1].point.z } : null;
  }

  // A depth on the body's centre line at height y: 0 at its back, 1 at its
  // front, 0.5 halfway.
  function bodyZ(y, f) {
    const n = S.zLine.length - 1;
    const i = clamp(Math.round((y - S.bounds.min.y) / S.H * n), 0, n);
    return S.zLine[i].back + (S.zLine[i].front - S.zLine[i].back) * f;
  }

  // A ray from the front at (x, y): the joint sits halfway between the
  // front-most and back-most surface it crosses. Not the first two hits: a
  // shirt over a body, or two overlapping parts, would pull it forward.
  function depthAt(x, y, fallback) {
    ray.set(V(x, y, S.bounds.max.z + S.H), BACK);
    const hits = ray.intersectObjects(S.meshes, false);
    if (!hits.length) return fallback;
    return (hits[0].point.z + hits[hits.length - 1].point.z) / 2;
  }

  // A ray from above at (x, z), for hands and arms: halfway through the first
  // slab it meets, so a leg further down never counts as the underside.
  function heightAt(x, z, fallback) {
    ray.set(V(x, S.bounds.max.y + S.H, z), DOWN);
    const hits = ray.intersectObjects(S.meshes, false);
    if (!hits.length) return fallback;
    const top = hits[0].point.y;
    let bottom = top;
    for (const h of hits) if (h.point.y > top - S.H * 0.05) bottom = h.point.y;
    return (top + bottom) / 2;
  }

  function profileZ(y) {
    const n = S.profile.length - 1;
    const t = clamp((y - S.bounds.min.y) / S.H, 0, 1) * n;
    const i = Math.floor(t), f = t - i;
    return i >= n ? S.profile[n] : S.profile[i] * (1 - f) + S.profile[i + 1] * f;
  }

  // The foot around an ankle, from the points near the floor: how far it
  // reaches forward and back, and how wide it is at a given depth.
  function footAround(ankle) {
    const F = S.feet, reach = S.H * 0.06;
    let front = -Infinity, back = Infinity;
    for (let i = 0; i < F.length; i += 3) {
      if (Math.abs(F[i] - ankle.x) > reach) continue;
      front = Math.max(front, F[i + 2]);
      back = Math.min(back, F[i + 2]);
    }
    if (!(front > ankle.z + S.H * 0.03)) front = ankle.z + S.H * 0.09;
    if (!(back < ankle.z)) back = ankle.z - S.H * 0.02;
    return { front, back };
  }
  function footWidthAt(ankle, z, sign) {
    const F = S.feet, reach = S.H * 0.06, band = S.H * 0.015;
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < F.length; i += 3) {
      if (Math.abs(F[i] - ankle.x) > reach || Math.abs(F[i + 2] - z) > band) continue;
      // never past the body's middle, where feet together would meet the other one
      if ((F[i] - S.cx) * sign < 0) continue;
      lo = Math.min(lo, F[i]);
      hi = Math.max(hi, F[i]);
    }
    return lo < hi ? { lo, hi } : { lo: ankle.x - S.H * 0.025, hi: ankle.x + S.H * 0.025 };
  }

  // The hand's frame from the wrist: `along` points down the forearm and out
  // through the fingers, `across` toward the thumb (the front, palms down).
  function handFrame(P) {
    const W = S.pos[P + 'Wrist'], E = S.pos[P + 'Elbow'];
    const along = W.clone().sub(E).normalize();
    const across = V(0, 0, 1).addScaledVector(along, -along.z).normalize();
    return { W, along, across };
  }

  // How far the hand reaches past the wrist, from the mesh.
  function handReach(P) {
    const { W, along } = handFrame(P);
    const pts = S.points, reach = S.H * 0.2, d = V();
    let length = 0;
    for (let i = 0; i < pts.length; i += 3) {
      d.set(pts[i] - W.x, pts[i + 1] - W.y, pts[i + 2] - W.z);
      const t = d.dot(along);
      if (t <= 0 || t > reach) continue;
      if (d.addScaledVector(along, -t).length() > S.H * 0.08) continue;
      length = Math.max(length, t);
    }
    if (length < S.H * 0.03) length = S.H * 0.1;
    return { length, tip: W.clone().addScaledVector(along, length) };
  }

  // Put b on the plane through a and c that holds the pole direction, bent
  // toward the pole by at least MIN_BEND of the limb: shoulder, elbow and
  // wrist (or hip, knee and ankle) stay coplanar and IK knows which way to go.
  function bendPlane(a, b, c, pole) {
    const u = c.clone().sub(a);
    const len = u.length();
    if (len < 1e-6) return b.clone();
    u.divideScalar(len);
    const p = pole.clone().addScaledVector(u, -pole.dot(u));
    if (p.lengthSq() < 1e-8) return b.clone();
    p.normalize();
    const n = u.clone().cross(p);
    const out = b.clone().addScaledVector(n, -b.clone().sub(a).dot(n));
    const bend = out.clone().sub(a).dot(p);
    if (bend < MIN_BEND * len) out.addScaledVector(p, MIN_BEND * len - bend);
    return out;
  }

  // The back of the hand: square to the palm through the wrist and the first
  // and last finger's knuckles, the same way up on both hands. Straight up
  // (palms down) when there are too few fingers to tell.
  function backOfHand(s, J) {
    const fingers = FINGER_SETS[S.fingers].filter((f) => f !== 'thumb');
    const W = J[s + 'Wrist'];
    const first = fingers.length > 1 && J[fingerKey(s, fingers[0], '01')];
    const last = fingers.length > 1 && J[fingerKey(s, fingers[fingers.length - 1], '01')];
    if (!W || !first || !last) return V(0, 1, 0);
    const back = first.clone().sub(W).cross(last.clone().sub(W)).multiplyScalar(SIGN[s]);
    return back.lengthSq() < 1e-12 ? V(0, 1, 0) : back.normalize();
  }

  // A finger's frame from its first marker: `along` toward its tip, `length`
  // away; `back` toward the back of the hand, square to that; `across`
  // square to both. A finger curls in its along-back plane.
  function fingerFrame(s, f, J) {
    const [a, z] = FINGER_ENDS[f === 'thumb' ? 'thumb' : 'other'];
    const from = J[fingerKey(s, f, a)];
    const along = J[fingerKey(s, f, z)].clone().sub(from);
    const length = along.length() || 1e-6;
    along.divideScalar(length);
    const back = V();
    for (const up of [backOfHand(s, J), V(0, 1, 0), V(1, 0, 0)]) {
      back.copy(up).addScaledVector(along, -up.dot(along));
      if (back.lengthSq() > 1e-8) break;
    }
    back.normalize();
    return { from, along, length, back, across: along.clone().cross(back) };
  }

  // Where a finger's middle joint sits: a share of the way from its first
  // marker to its tip, plus shares of that length toward the back of the hand
  // and across, so it follows when either marker moves. Only the thumb's go
  // across: a finger's joints from the knuckle to the tip stay in the plane it
  // curls in, while its metacarpal and the cups go anywhere.
  function middleAt(s, f, n, J) {
    const F = fingerFrame(s, f, J);
    const m = S.mids[fingerKey(s, f, n)] || { t: FINGER_STEPS[f === 'thumb' ? 'thumb' : 'other'][n], b: 0, c: 0 };
    return F.from.clone().addScaledVector(F.along, m.t * F.length)
      .addScaledVector(F.back, m.b * F.length).addScaledVector(F.across, m.c * F.length);
  }

  // ------------------------------------------------------- auto placement
  // Placement reads landmarks off the mesh, then puts each joint where it sits
  // in a human body relative to them, not relative to the body's height:
  //   crotch  the lowest point where a ray down the middle meets the body
  //   throat  the thinnest point front to back between the chest and the head
  //           (not the narrowest side to side: a muscular neck is wider than
  //           the face above it)
  //   arms    the points outside the torso, followed along their own axis:
  //           the shoulder where the arm meets the torso, the wrist at the
  //           forearm's thinnest point, the elbow halfway between
  //   legs    each leg's slice centre at the hip, knee and ankle; each foot's
  //           inner and outer edge across from the ball
  //   eyes    the eyeballs, when the model has them as parts of their own
  // The offsets from those landmarks come from real skeletons: the Mutant
  // Tools human template and Quaternius' base characters.
  const AUTO_STEPS = [
    ['Measuring the body', () => {}],
    ['Finding the crotch and the throat', () => findTrunk()],
    ['Following the arms to the wrists', () => findArms()],
    ['Finding the hips, knees and feet', () => findLegs()],
    ['Fitting the hands and fingers', () => { for (const s of SIDES) guessFingers(s); }],
    ['Placing the spine, neck and head', () => placeSpine()],
    ['Finding the eyes', () => findEyes()],
  ];
  let placing = false;

  async function autoPlace() {
    if (placing || !S.pivot) return;
    placing = true;
    const panel = $('[data-auto]'), list = $('[data-auto-steps]'), bar = $('[data-auto-bar]');
    list.innerHTML = AUTO_STEPS.map(([label]) => '<li>' + label + '</li>').join('');
    panel.hidden = false;
    root.classList.add('is-placing');
    skeleton.visible = false;
    const items = [...list.children];
    S.pos = {};
    S.spineOff = {};
    S.mids = {};
    S.joints = {};
    invalidate();
    for (let i = 0; i < AUTO_STEPS.length; i++) {
      items[i].className = 'is-on';
      bar.style.width = (i / AUTO_STEPS.length * 100) + '%';
      await new Promise((ok) => setTimeout(ok, 180)); // long enough to read, and to paint
      AUTO_STEPS[i][1]();
      items[i].className = 'is-done';
    }
    bar.style.width = '100%';
    await new Promise((ok) => setTimeout(ok, 220));
    panel.hidden = true;
    root.classList.remove('is-placing');
    placing = false;
    skeleton.visible = $('[data-bones]').getAttribute('aria-pressed') === 'true';
    select(null);
    rebuild();
    fitView(true);
    invalidate();
  }

  // The torso's half-width at y: the run of the slice that holds the centre
  // line, so an arm hanging close by is not counted as torso.
  function torsoHalf(y) {
    // rays from inside the body out to each side stop at the torso's own
    // skin, whatever hangs beside it
    const from = V(S.cx, y, bodyZ(y, 0.5));
    let half = S.H * 0.05;
    for (const dir of [V(1, 0, 0), V(-1, 0, 0)]) {
      ray.set(from, dir);
      const hit = ray.intersectObjects(S.meshes, false)[0];
      if (hit) half = Math.max(half, hit.distance);
    }
    return half;
  }

  function findTrunk() {
    const y0 = S.bounds.min.y, H = S.H, cx = S.cx, top = S.bounds.max.y;
    let crotch = y0 + 0.48 * H;
    for (let y = y0 + 0.3 * H; y < y0 + 0.62 * H; y += H * 0.004) {
      if (depthAt(cx, y, null) !== null) { crotch = y; break; }
    }
    let throat = y0 + 0.86 * H, thin = Infinity;
    for (let y = crotch + (top - crotch) * 0.6; y < top - 0.07 * H; y += H * 0.004) {
      const z = rayZ(cx, y);
      if (z && z.front - z.back < thin) { thin = z.front - z.back; throat = y; }
    }
    S.land = { crotch, throat };
    S.pos.groin = V(cx, crotch, bodyZ(crotch, 0.5));
    S.pos.chin = V(cx, throat + 0.015 * H, bodyZ(throat + 0.015 * H, 0.5));
  }

  // Each arm: a first line from where the arm meets the torso to the hand's
  // furthest point, the points close to that line (so hips and thighs never
  // count), and the arm's cross-section slice by slice along it.
  function findArms() {
    const H = S.H, cx = S.cx, P = S.points, { throat } = S.land;
    const half = torsoHalf(throat - 0.12 * H);
    for (const s of SIDES) {
      const sign = SIGN[s];
      const y = throat - 0.055 * H;
      const root = V(cx + sign * half, y, bodyZ(y, 0.45));
      let tip = null;
      for (let i = 0; i < P.length; i += 3) {
        if ((P[i] - cx) * sign > (tip ? (tip.x - cx) * sign : -Infinity)) tip = V(P[i], P[i + 1], P[i + 2]);
      }
      const d = tip ? tip.clone().sub(root) : V();
      const span = d.length();
      if (!tip || span < 0.1 * H) { guessArm(s); continue; }
      d.divideScalar(span);
      // slices along the line: each slice's centre and how thick the arm is
      const step = 0.01 * H, nb = Math.ceil(span / step), reach = 0.07 * H;
      const bins = Array.from({ length: nb + 1 }, () => ({ c: V(), n: 0, r: 0 }));
      const q = V(), hits = [];
      for (let i = 0; i < P.length; i += 3) {
        q.set(P[i] - root.x, P[i + 1] - root.y, P[i + 2] - root.z);
        const t = q.dot(d);
        if (t < 0 || t > span) continue;
        if (q.addScaledVector(d, -t).length() > reach) continue;
        const b = Math.floor(t / step);
        bins[b].c.add(V(P[i], P[i + 1], P[i + 2]));
        bins[b].n++;
        hits.push(i, b);
      }
      for (const b of bins) if (b.n) b.c.divideScalar(b.n);
      for (let k = 0; k < hits.length; k += 2) {
        const i = hits[k], b = bins[hits[k + 1]];
        q.set(P[i] - b.c.x, P[i + 1] - b.c.y, P[i + 2] - b.c.z);
        b.r += q.addScaledVector(d, -q.dot(d)).length() / b.n;
      }
      const centre = (t) => {
        let i = clamp(Math.round(t / step), 0, nb);
        while (i > 0 && !bins[i].n) i--;
        return bins[i].n ? bins[i].c.clone() : root.clone().addScaledVector(d, t);
      };
      // wrist: where the forearm is thinnest, at the hand's end of that stretch
      let wristT = 0.72 * span, thinnest = Infinity;
      const usable = (i) => { const f = (i * step) / span; return f >= 0.55 && f <= 0.8 && bins[i].n >= 6; };
      for (let i = 0; i <= nb; i++) if (usable(i) && bins[i].r < thinnest) thinnest = bins[i].r;
      for (let i = 0; i <= nb; i++) if (usable(i) && bins[i].r <= thinnest * 1.08) wristT = i * step;
      // shoulder: the upper arm's centre line, carried back to the torso
      const avg = (f0, f1) => {
        const a = V();
        let n = 0;
        for (let i = 0; i <= nb; i++) {
          const f = (i * step) / wristT;
          if (f >= f0 && f <= f1 && bins[i].n) { a.add(bins[i].c); n++; }
        }
        return n ? a.divideScalar(n) : null;
      };
      const A = avg(0.2, 0.3), B = avg(0.38, 0.48);
      let shoulder = root.clone();
      if (A && B) {
        const u = B.clone().sub(A).normalize();
        const along = (root.x - A.x) / (u.x || 1e-6); // back to the torso's edge
        if (along < 0 && along > -0.25 * H) shoulder = A.clone().addScaledVector(u, along);
      }
      const wrist = centre(wristT);
      const back = shoulder.clone().sub(root).dot(d);
      const elbow = centre(back + (wristT - back) * 0.5);
      Object.assign(S.pos, { [s + 'Shoulder']: shoulder, [s + 'Elbow']: elbow, [s + 'Wrist']: wrist });
    }
  }

  // When an arm cannot be told apart from the torso: proportions alone.
  function guessArm(s) {
    const H = S.H, { throat } = S.land, y = throat - 0.055 * H;
    const shoulder = V(S.cx + SIGN[s] * 0.115 * H, y, bodyZ(y, 0.4));
    S.pos[s + 'Shoulder'] = shoulder;
    S.pos[s + 'Elbow'] = shoulder.clone().add(V(SIGN[s] * 0.06 * H, -0.12 * H, 0));
    S.pos[s + 'Wrist'] = shoulder.clone().add(V(SIGN[s] * 0.12 * H, -0.24 * H, 0));
  }

  function findLegs() {
    const y0 = S.bounds.min.y, H = S.H, { crotch } = S.land;
    for (const s of SIDES) {
      const sign = SIGN[s];
      const legX = (y) => sliceMid(y, sign, 0.2) ?? S.cx + sign * 0.06 * H;
      const hip = V(legX(crotch - 0.05 * H), crotch + 0.035 * H, 0);
      const thigh = rayZ(hip.x, crotch - 0.03 * H);
      hip.z = thigh ? thigh.back + (thigh.front - thigh.back) * 0.42 : profileZ(crotch);
      const ax = S.ankleX[s] ?? legX(y0 + 0.09 * H);
      const ankle = V(ax, y0 + 0.052 * H, depthAt(ax, y0 + 0.09 * H, hip.z));
      const ky = ankle.y + (hip.y - ankle.y) * 0.53;
      const kx = legX(ky);
      const knee = V(kx, ky, depthAt(kx, ky, hip.z));
      Object.assign(S.pos, { [s + 'Hip']: hip, [s + 'Knee']: knee, [s + 'Ankle']: ankle });
      S.pos[s + 'Pelvis'] = V(hip.x, hip.y + 0.058 * H, hip.z);
      const foot = footAround(ankle);
      S.pos[s + 'Foot_Ball'] = V(ankle.x, y0 + 0.016 * H, ankle.z + (foot.front - ankle.z) * 0.62);
      S.pos[s + 'Foot_Toes'] = V(ankle.x, y0, foot.front);
      S.pos[s + 'Foot_Heel'] = V(ankle.x, y0, foot.back);
      // the pivots it rocks on: its inner and outer edge across from the ball
      const ball = S.pos[s + 'Foot_Ball'], wide = footWidthAt(ankle, ball.z, sign);
      S.pos[s + 'Foot_In'] = V(sign > 0 ? wide.lo : wide.hi, y0, ball.z);
      S.pos[s + 'Foot_Out'] = V(sign > 0 ? wide.hi : wide.lo, y0, ball.z);
    }
  }

  // Fingers fan out across the hand's width at the fingertips, knuckles a bit
  // under halfway from the wrist. The thumb's tip is the hand's point that
  // reaches furthest toward the front. Metacarpals and cups sit between the
  // wrist and the fingers.
  function guessFingers(s) {
    // the middle joints go back to their usual places along each finger
    for (const key in S.mids) if (key.startsWith(s)) delete S.mids[key];
    const { W, along, across } = handFrame(s);
    const { length } = handReach(s);
    const pts = S.points, d = V();
    let lo = Infinity, hi = -Infinity, thumbTip = null, reachOut = -Infinity;
    for (let i = 0; i < pts.length; i += 3) {
      d.set(pts[i] - W.x, pts[i + 1] - W.y, pts[i + 2] - W.z);
      const t = d.dot(along);
      if (t < 0 || t > length) continue;
      const u = d.dot(across);
      if (d.clone().addScaledVector(along, -t).length() > S.H * 0.09) continue;
      if (t > length * 0.15 && t < length * 0.8 && u > reachOut) { reachOut = u; thumbTip = V(pts[i], pts[i + 1], pts[i + 2]); }
      if (t < length * 0.75 || Math.abs(u) > S.H * 0.08) continue;
      lo = Math.min(lo, u);
      hi = Math.max(hi, u);
    }
    if (!(hi > lo)) { lo = -0.03 * S.H; hi = 0.03 * S.H; }
    const width = hi - lo;
    const recentre = (p) => { p.y = heightAt(p.x, p.z, p.y); return p; };
    const at = (t, u) => recentre(W.clone().addScaledVector(along, t * length).addScaledVector(across, u));
    const reach = { index: 0.93, middle: 1, ring: 0.95, pinky: 0.82 };
    const fingers = FINGER_SETS[S.fingers || 5].filter((f) => f !== 'thumb');
    fingers.forEach((f, i) => {
      const u = hi - width * (i + 0.5) / fingers.length;
      S.pos[fingerKey(s, f, '01')] = at(0.45, u);
      S.pos[fingerKey(s, f, '04')] = at(reach[f] * 0.97, u);
      S.pos[fingerKey(s, f, '00')] = W.clone().lerp(S.pos[fingerKey(s, f, '01')], 0.5);
    });
    const base = S.pos[fingerKey(s, 'thumb', '00')] = at(0.12, hi - width * 0.15);
    S.pos[fingerKey(s, 'thumb', '03')] = thumbTip && reachOut > hi
      ? recentre(thumbTip.lerp(base, 0.08))
      : at(0.55, hi + width * 0.35);
    S.pos[s + 'Hand_InnerCup'] = W.clone().lerp(base, 0.8);
    const outer = ['ring', 'pinky'].filter((f) => fingers.includes(f));
    const mid = V();
    outer.forEach((f) => mid.add(S.pos[fingerKey(s, f, '00')]));
    S.pos[s + 'Hand_OutterCup'] = outer.length ? W.clone().lerp(mid.divideScalar(outer.length), 0.4) : W.clone();
  }

  // Spine, neck, head and clavicles, from the crotch and the throat. Spine
  // joints sit a little behind the body's middle, where the vertebrae are.
  function placeSpine() {
    const H = S.H, M = S.pos, { crotch, throat } = S.land, top = S.bounds.max.y;
    const midX = (y) => M.groin.x + (M.chin.x - M.groin.x) * ((y - M.groin.y) / (M.chin.y - M.groin.y || 1));
    const at = (y, f) => V(midX(y), y, bodyZ(y, f));
    M.Spine_Root = at(crotch + 0.03 * H, 0.42);
    M.Neck = at(throat - 0.02 * H, 0.45);
    for (const [key, f] of SPINE) {
      const y = M.Spine_Root.y + (M.Neck.y - M.Spine_Root.y) * f;
      S.spineOff[key] = at(y, 0.42).sub(M.Spine_Root.clone().lerp(M.Neck, f));
    }
    M.Head = at(throat + 0.024 * H, 0.45);
    M.HeadEnd = V(M.Head.x, top, M.Head.z);
    for (const s of SIDES) {
      const y = M[s + 'Shoulder'].y + 0.02 * H;
      M[s + 'Clavicle'] = V(midX(y) + SIGN[s] * 0.017 * H, y, bodyZ(y, 0.85));
    }
  }

  // The eyes: the middle of each eyeball when the model has them as parts of
  // their own, else where eyes sit in a head: about halfway from the chin to
  // the top, a fifth of the forehead's width out from the middle, an
  // eyeball's radius behind the face.
  function findEyes() {
    const M = S.pos, chin = M.chin.y, top = M.HeadEnd.y, tall = top - chin, mid = M.Head.x;
    const found = eyeballs(chin, top, mid);
    S.eyeParts = found.parts;
    const brow = headHalf(chin + tall * 0.65, mid);
    for (const s of SIDES) {
      if (found[s]) {
        M[s + 'Eyes'] = found[s];
        continue;
      }
      const x = mid + SIGN[s] * brow * 0.45, y = chin + tall * 0.48;
      const hit = rayZ(x, y);
      M[s + 'Eyes'] = V(x, y, hit ? hit.front - brow * 0.16 : bodyZ(y, 0.75));
    }
  }

  // Eyeballs modelled as parts of their own: a mesh inside the head whose
  // half on a side is about as tall and deep as it is wide, small next to the
  // head and above the mouth. Eyebrows, lashes and teeth are too flat. Every
  // such mesh centred on a chosen eyeball is one of its `parts`, a cornea
  // modelled over it too: the eye joint carries their skin.
  function eyeballs(chin, top, mid) {
    const tall = top - chin, round = [], best = {}, v = V();
    for (const m of S.meshes) {
      const halves = { L_: new THREE.Box3(), R_: new THREE.Box3() };
      const pos = m.geometry.attributes.position;
      for (let i = 0; i < pos.count; i++) {
        m.getVertexPosition(i, v).applyMatrix4(m.matrixWorld);
        halves[v.x >= mid ? 'L_' : 'R_'].expandByPoint(v);
      }
      const all = halves.L_.clone().union(halves.R_);
      if (all.min.y < chin - tall * 0.2 || all.max.y > top + tall * 0.1) continue;
      for (const s of SIDES) {
        if (halves[s].isEmpty()) continue;
        const size = halves[s].getSize(V()), at = halves[s].getCenter(V());
        const big = Math.max(size.x, size.y, size.z), ratio = Math.min(size.x, size.y, size.z) / (big || 1);
        if (big > tall * 0.3 || ratio < 0.6 || at.y < chin + tall * 0.3 || Math.abs(at.x - mid) > tall * 0.5) continue;
        const score = ratio + (/eye/i.test(m.name) && !/brow|lash|lid/i.test(m.name) ? 1 : 0);
        round.push({ mesh: m, s, at, big });
        if (!best[s] || score > best[s].score) best[s] = { score, at, big };
      }
    }
    const parts = new Set(round.filter((r) => best[r.s] && r.at.distanceTo(best[r.s].at) < best[r.s].big * 0.5)
      .map((r) => r.mesh));
    return { L_: best.L_ && best.L_.at, R_: best.R_ && best.R_.at, parts };
  }

  // Half the head's width at height y.
  function headHalf(y, mid) {
    const P = S.points, band = S.H * 0.01;
    let half = 0;
    for (let i = 0; i < P.length; i += 3) {
      const out = Math.abs(P[i] - mid);
      if (out < S.H * 0.12 && Math.abs(P[i + 1] - y) < band) half = Math.max(half, out);
    }
    return half || S.H * 0.045;
  }

  // ------------------------------------------------------------ skeleton
  // Everything the page works out rather than stores: the spine's inner
  // joints, the bend planes, the middle finger joints, the foot pivots' floor,
  // the twists.
  function derive() {
    const M = S.pos, J = {}, y0 = S.bounds.min.y;
    for (const k in M) J[k] = M[k].clone();
    for (const [key, f] of SPINE) J[key] = M.Spine_Root.clone().lerp(M.Neck, f).add(S.spineOff[key] || V());
    J.Spine_End = J.Neck.clone();
    for (const s of SIDES) {
      // the elbow and knee stay on their limb's bend plane; that is a rule of
      // the joint itself, so it is written back to where it is stored
      M[s + 'Elbow'].copy(bendPlane(M[s + 'Shoulder'], M[s + 'Elbow'], M[s + 'Wrist'], ELBOW_POLE));
      M[s + 'Knee'].copy(bendPlane(M[s + 'Hip'], M[s + 'Knee'], M[s + 'Ankle'], KNEE_POLE));
      J[s + 'Elbow'] = M[s + 'Elbow'].clone();
      J[s + 'Knee'] = M[s + 'Knee'].clone();
      const W = J[s + 'Wrist'];
      J[s + 'Hand_End'] = W.clone().addScaledVector(W.clone().sub(J[s + 'Elbow']), 0.5);
      for (const f of FINGER_SETS[S.fingers]) {
        for (const n in FINGER_STEPS[f === 'thumb' ? 'thumb' : 'other']) J[fingerKey(s, f, n)] = middleAt(s, f, n, J);
      }
      const ball = J[s + 'Foot_Ball'], heel = J[s + 'Foot_Heel'];
      J[s + 'Foot_BallFloor'] = V(ball.x, y0, ball.z);
      J[s + 'Foot_HeelMid'] = heel.clone().lerp(J[s + 'Foot_BallFloor'], 0.3);
      // the rock's pivots stay on the floor, across from the ball
      for (const g of ['Foot_In', 'Foot_Out']) {
        if (!M[s + g]) continue;
        M[s + g].set(M[s + g].x, y0, ball.z);
        J[s + g] = M[s + g].clone();
      }
      for (const [from, to] of TWIST_BONES) {
        for (let i = 1; i <= S.twists; i++) {
          J[twistKey(s, from, i)] = J[s + from].clone().lerp(J[s + to], i / (S.twists + 1));
        }
      }
    }
    return J;
  }

  function rebuild() {
    S.list = jointList(S.fingers, S.twists);
    S.joints = derive();
    const pos = bones.geometry.attributes.position;
    const used = new Set();
    S.list.forEach(([key, parent], i) => {
      used.add(key);
      balls[key].position.copy(S.joints[key]);
      const a = S.joints[parent || key], b = S.joints[key];
      pos.setXYZ(i * 2, a.x, a.y, a.z);
      pos.setXYZ(i * 2 + 1, b.x, b.y, b.z);
    });
    for (const key of PIVOTS) {
      if (!S.joints[key]) continue;
      used.add(key);
      balls[key].position.copy(S.joints[key]);
    }
    for (const key in balls) balls[key].visible = used.has(key);
    pos.needsUpdate = true;
    bones.geometry.setDrawRange(0, S.list.length * 2);
    $('[data-count]').textContent = S.list.length + ' joints';
    // weights, and a running test, belong to the skeleton they were made for
    if (test.rig) stopTest(true);
    if (S.weights) {
      S.weights = null;
      showWeights(false);
    }
    skinStatus();
  }

  // Where a point is now.
  const pointAt = (id) => S.joints[id] || S.pos[id];

  // ------------------------------------------------------------- points
  const els = {};
  for (const pt of POINTS) {
    const el = document.createElement('button');
    el.type = 'button';
    el.className = 'mt-marker' + (pt.tip ? ' mt-marker--tip' : '') + (pt.kind === 'handle' ? ' mt-marker--handle' : '');
    el.style.setProperty('--c', pt.color);
    el.dataset.label = pt.label;
    el.setAttribute('aria-label', pt.label + (pt.kind === 'handle' ? ' handle' : ' marker') +
      '. Drag it, or use the arrow keys.');
    layer.append(el);
    els[pt.id] = el;

    el.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      el.setPointerCapture(e.pointerId);
      el.classList.add('is-drag');
      select(pt.id);
    });
    el.addEventListener('pointermove', (e) => {
      if (el.hasPointerCapture(e.pointerId)) queueDrag(pt.id, e.clientX, e.clientY);
    });
    const end = (e) => {
      if (el.hasPointerCapture(e.pointerId)) el.releasePointerCapture(e.pointerId);
      el.classList.remove('is-drag');
    };
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);
    el.addEventListener('focus', () => select(pt.id));
    el.addEventListener('keydown', (e) => {
      const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
      if (!dir) return;
      e.preventDefault();
      const step = (S.view === 'top' ? handReach(S.hand).length * 0.1 : S.H * 0.02) * (e.shiftKey ? 1 : 0.2);
      const right = V().setFromMatrixColumn(ortho.matrixWorld, 0);
      const up = V().setFromMatrixColumn(ortho.matrixWorld, 1);
      movePoint(pt.id, pointAt(pt.id).clone()
        .addScaledVector(right, dir[0] * step).addScaledVector(up, dir[1] * step));
    });
  }

  // The body list in step 2 and the finger list in step 3. A finger's row
  // picks its base marker on whichever hand the top view is showing.
  function listRow(label, color, onClick) {
    const li = document.createElement('li');
    li.innerHTML = '<button type="button" aria-pressed="false"><span class="mt-swatch"></span></button>';
    const btn = li.firstChild;
    btn.querySelector('.mt-swatch').style.setProperty('--c', color);
    btn.append(label);
    btn.addEventListener('click', onClick);
    return li;
  }
  const bodyList = $('[data-marker-list]');
  for (const id of BODY_MARKERS) {
    const li = listRow(POINT[id].label, POINT[id].color, () => {
      if (S.view === 'top' || S.view === '3d') setView('front');
      els[id].focus();
    });
    li.firstChild.dataset.point = id;
    bodyList.append(li);
  }
  const fingerList = $('[data-finger-list]');
  for (const f of FINGERS) {
    const li = listRow(f.label, f.color, () => {
      if (S.view !== 'top') setView('top');
      els[fingerKey(S.hand, f.id, FINGER_ENDS[f.id === 'thumb' ? 'thumb' : 'other'][0])].focus();
    });
    li.firstChild.dataset.finger = f.id;
    fingerList.append(li);
  }

  function select(id) {
    S.selected = id;
    for (const k in els) els[k].classList.toggle('is-on', k === id);
    bodyList.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.point === id)));
    const finger = id && POINT[id].finger;
    fingerList.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.finger === finger)));
    // with weights on screen, picking a joint shows that joint's weights
    if (S.weights && $('[data-weights]').getAttribute('aria-pressed') === 'true') {
      paintWeights();
      invalidate();
    }
  }

  let pending = null;
  function queueDrag(id, x, y) {
    const first = !pending;
    pending = { id, x, y };
    if (first) requestAnimationFrame(() => {
      const r = renderer.domElement.getBoundingClientRect();
      const p = V(((pending.x - r.left) / r.width) * 2 - 1, -((pending.y - r.top) / r.height) * 2 + 1, 0)
        .unproject(ortho);
      movePoint(pending.id, p);
      pending = null;
    });
  }

  // Where a drag to p takes a point in the current view. Front view moves it
  // across the body, side view forward and back, top view over the hand; the
  // third axis is found from the mesh or kept, as the point asks.
  function dragTarget(pt, from, p) {
    const b = S.bounds, pad = S.H * 0.1;
    const X = clamp(p.x, b.min.x - pad, b.max.x + pad);
    const Y = clamp(p.y, b.min.y - pad, b.max.y + pad);
    const Z = clamp(p.z, b.min.z - pad, b.max.z + pad);
    if (S.view === 'front') return V(X, Y, pt.front === 'center' ? depthAt(X, Y, from.z) : from.z);
    if (S.view === 'side') return V(from.x, Y, Z);
    return V(X, pt.top === 'height' ? heightAt(X, Z, from.y) : from.y, Z);
  }

  // Moving a point carries everything placed under it (PLACE_PARENT) by the
  // same amount, and nothing above it.
  function shift(id, d, moved) {
    moved.add(id);
    if (SPINE_KEYS.has(id)) S.spineOff[id] = (S.spineOff[id] || V()).add(d);
    else if (S.pos[id]) S.pos[id].add(d);
    for (const child of PLACE_CHILDREN[id] || []) shift(child, d, moved);
  }
  const spineNow = () => Object.fromEntries(SPINE.map(([k, f]) =>
    [k, S.pos.Spine_Root.clone().lerp(S.pos.Neck, f).add(S.spineOff[k] || V())]));

  // A finger's middle joint keeps where it is dragged to as its place in the
  // finger's frame (see middleAt); the other hand's twin takes it mirrored.
  function moveMiddle(id, to) {
    const f = POINT[id].finger, F = fingerFrame(sideOf(id), f, S.joints);
    const d = to.clone().sub(F.from).divideScalar(F.length);
    const m = S.mids[id] = { t: d.dot(F.along), b: d.dot(F.back), c: f === 'thumb' ? d.dot(F.across) : 0 };
    if ($('[data-mirror]').checked) S.mids[twinOf(id)] = { t: m.t, b: m.b, c: -m.c };
    rebuild();
    invalidate();
  }

  function movePoint(id, p) {
    const pt = POINT[id];
    if (pt.middle) return moveMiddle(id, dragTarget(pt, pointAt(id).clone(), p));
    const before = spineNow(), moved = new Set();
    const from = pointAt(id).clone();
    const to = dragTarget(pt, from, p);
    shift(id, to.clone().sub(from), moved);

    // the other side follows, mirrored across the body's centre line
    const twin = twinOf(id);
    if (twin && $('[data-mirror]').checked) {
      const axis = (S.pos.chin.x + S.pos.groin.x) / 2;
      const o = V(2 * axis - to.x, to.y, to.z);
      if (S.view === 'front' && pt.front === 'center') o.z = depthAt(o.x, o.y, to.z);
      if (S.view === 'top' && pt.top === 'height') o.y = heightAt(o.x, o.z, to.y);
      shift(twin, o.sub(pointAt(twin)), moved);
    }

    // when the root or the neck moved, the spine re-spaced between them, and
    // what hangs off its inner joints (the clavicles, so the arms) goes along
    const after = spineNow();
    for (const [key] of SPINE) {
      if (moved.has(key)) continue;
      const d = after[key].sub(before[key]);
      if (d.lengthSq() > 0) for (const child of PLACE_CHILDREN[key] || []) shift(child, d, moved);
    }
    rebuild();
    invalidate();
  }

  function shown(pt) {
    if (!S.pivot || placing || !pointAt(pt.id) || S.view === '3d' || !pt.views.includes(S.view)) return false;
    if (pt.finger && !pt.finger.split(' ').some((f) => FINGER_SETS[S.fingers].includes(f))) return false;
    const s = sideOf(pt.id);
    if (S.view === 'top') return s === S.hand;
    return !(S.view === 'side' && s === 'R_' && $('[data-mirror]').checked);
  }

  function placePoints() {
    const { w, h } = size();
    for (const pt of POINTS) {
      const el = els[pt.id];
      el.hidden = !shown(pt);
      if (el.hidden) continue;
      const p = pointAt(pt.id).clone().project(ortho);
      el.style.left = ((p.x + 1) / 2 * w).toFixed(1) + 'px';
      el.style.top = ((1 - p.y) / 2 * h).toFixed(1) + 'px';
    }
  }

  // In the flat views the wheel zooms toward the cursor and dragging empty
  // space pans, so small parts like fingers and toes can be worked up close.
  const ndcOf = (e) => {
    const r = renderer.domElement.getBoundingClientRect();
    return V(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1, 0);
  };
  stage.addEventListener('wheel', (e) => {
    if (S.view === '3d' || !S.pivot) return;
    e.preventDefault();
    const ndc = ndcOf(e);
    const before = ndc.clone().unproject(ortho);
    ortho.zoom = clamp(ortho.zoom * Math.exp(-e.deltaY * 0.0015), 0.5, 25);
    ortho.updateProjectionMatrix();
    ortho.position.add(before.sub(ndc.clone().unproject(ortho)));
    ortho.updateMatrixWorld();
    invalidate();
  }, { passive: false });
  let pan = null;
  renderer.domElement.addEventListener('pointerdown', (e) => {
    if (S.view === '3d' || !S.pivot || e.pointerType !== 'mouse') return;
    renderer.domElement.setPointerCapture(e.pointerId);
    pan = ndcOf(e).unproject(ortho);
  });
  renderer.domElement.addEventListener('pointermove', (e) => {
    if (!pan) return;
    ortho.position.add(pan.clone().sub(ndcOf(e).unproject(ortho)));
    ortho.updateMatrixWorld();
    invalidate();
  });
  const endPan = () => { pan = null; };
  renderer.domElement.addEventListener('pointerup', endPan);
  renderer.domElement.addEventListener('pointercancel', endPan);

  // -------------------------------------------------------------- views
  function setView(view) {
    S.view = view;
    root.dataset.view = view;
    $$('[data-view-btn]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.viewBtn === view)));
    controls.enabled = view === '3d';
    $('[data-hint]').textContent = HINTS[view];
    fitView(true);
    invalidate();
  }
  $$('[data-view-btn]').forEach((b) => b.addEventListener('click', () => setView(b.dataset.viewBtn)));

  function setHand(s) {
    S.hand = s;
    $$('[data-hand-btn]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.handBtn === s)));
    if (S.view === 'top') fitView(false);
    invalidate();
  }
  $$('[data-hand-btn]').forEach((b) => b.addEventListener('click', () => setHand(b.dataset.handBtn)));

  function toggle(sel, apply) {
    const b = $(sel);
    b.addEventListener('click', () => {
      const on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', String(on));
      apply(on);
      invalidate();
    });
  }
  toggle('[data-xray]', (on) => { clay.opacity = on ? 0.35 : 1; clay.depthWrite = !on; });
  toggle('[data-bones]', (on) => { skeleton.visible = on && !!S.pivot; });
  toggle('[data-topology]', (on) => showTopology(on));
  $('[data-anim]').addEventListener('change', (e) => playTest(e.target.value));
  $('[data-weights]').addEventListener('click', () => {
    const on = $('[data-weights]').getAttribute('aria-pressed') !== 'true';
    if (on) busySkin('Calculating weights…');
    setTimeout(() => showWeights(on), 30);
  });
  toggle('[data-upaxis]', (on) => { S.up = on ? 'z' : 'y'; orient(); });
  $('[data-turn]').addEventListener('click', () => { S.turn = (S.turn + 1) % 4; orient(); });
  $('[data-reset]').addEventListener('click', autoPlace);
  $$('[data-autoplace]').forEach((b) => b.addEventListener('click', autoPlace));
  $('[data-reset-fingers]').addEventListener('click', () => {
    for (const s of SIDES) guessFingers(s);
    rebuild();
    invalidate();
  });
  $('[data-mirror]').addEventListener('change', invalidate);
  $('[data-fingers]').addEventListener('change', (e) => {
    S.fingers = Number(e.target.value);
    fingerList.querySelectorAll('button').forEach((b) => {
      b.parentNode.hidden = !FINGER_SETS[S.fingers].includes(b.dataset.finger);
    });
    if (S.pivot) {
      for (const s of SIDES) guessFingers(s);
      rebuild();
      invalidate();
    }
  });
  $('[data-twists]').addEventListener('change', (e) => {
    S.twists = Number(e.target.value);
    if (S.pivot) {
      rebuild();
      invalidate();
    }
  });
  $$('[data-go-view]').forEach((b) => b.addEventListener('click', () => setView(b.dataset.goView)));

  // --------------------------------------------------------------- input
  const file = $('[data-file]');
  $$('[data-pick]').forEach((b) => b.addEventListener('click', () => file.click()));
  file.addEventListener('change', () => { loadFile(file.files[0]); file.value = ''; });
  $$('[data-demo]').forEach((b) => b.addEventListener('click', loadExample));

  for (const zone of [stage, $('[data-dropzone]')]) {
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('is-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('is-over'));
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('is-over');
      loadFile(e.dataTransfer.files[0]);
    });
  }

  function busy(text) {
    dropMsg.textContent = text || dropMsg.dataset.idle;
    root.classList.toggle('is-busy', !!text);
  }
  function showError(text) {
    errorBox.hidden = !text;
    errorBox.querySelector('p').textContent = text;
  }

  // ------------------------------------------------------------ skinning
  // Each vertex goes to the nearest bone it can see from inside the mesh: a
  // ray from the bone to the vertex must not leave the surface on the way, so
  // a hand never claims the hip it hangs beside. Weights then blend across
  // each joint, are smoothed over the surface, and keep at most four bones.
  const MAX_INFLUENCES = 4;
  const BLEND_ZONE = 0.2;       // of a bone's length, either side of a joint
  const SMOOTH_PASSES = 2;
  const vis = new THREE.Raycaster();
  vis.firstHitOnly = true;
  const smoothstep = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };

  // Bones as segments, each owned by the joint it starts from: the joint
  // whose weights the vertices along it receive. Leaf joints own nothing.
  // A long bone with twist joints hands its weight down the bone through
  // them: `stations` are the joints along it and where each sits.
  function boneSegments() {
    const parentOf = Object.fromEntries(S.list.filter(([k]) => !isTwist(k)));
    const owners = new Set(S.list.filter(([k]) => !isTwist(k)).map(([, p]) => p).filter(Boolean));
    const stationsOf = (from, to) => {
      const st = [{ key: from, t: 0 }];
      const P = sideOf(from), bone = TWIST_BONES.find(([f, t]) => P + f === from && P + t === to);
      if (bone) for (let i = 1; i <= S.twists; i++) st.push({ key: twistKey(P, bone[0], i), t: i / (S.twists + 1) });
      return st;
    };
    const segs = [];
    for (const [key, parent] of S.list) {
      if (!parent || isTwist(key)) continue;
      const a = S.joints[parent], b = S.joints[key];
      const len = a.distanceTo(b);
      if (len < 1e-6) continue;
      const grand = parentOf[parent];
      const above = grand ? stationsOf(grand, parent) : null;
      segs.push({
        owner: parent, a, b, len, stations: stationsOf(parent, key),
        up: above ? above[above.length - 1].key : null, down: owners.has(key) ? key : null,
      });
    }
    return segs;
  }

  // Merge a mesh's vertices that share a position (three.js splits them at
  // UV and normal seams) into nodes, and link nodes that share a triangle.
  function weld(m) {
    const pos = m.geometry.attributes.position, index = m.geometry.index;
    const box = new THREE.Box3().setFromBufferAttribute(pos);
    const q = Math.max(box.getSize(V()).length(), 1e-9) * 1e-5;
    const key = (x, y, z) => Math.round(x / q) + ',' + Math.round(y / q) + ',' + Math.round(z / q);
    const nodeOfKey = new Map(), vToNode = new Int32Array(pos.count), world = [];
    const v = V();
    for (let i = 0; i < pos.count; i++) {
      const k = key(pos.getX(i), pos.getY(i), pos.getZ(i));
      let n = nodeOfKey.get(k);
      if (n === undefined) {
        n = world.length;
        nodeOfKey.set(k, n);
        world.push(m.getVertexPosition(i, v).applyMatrix4(m.matrixWorld).clone());
      }
      vToNode[i] = n;
    }
    const near = world.map(() => new Set());
    const tris = index ? index.count / 3 : pos.count / 3;
    for (let t = 0; t < tris; t++) {
      const ids = [0, 1, 2].map((c) => vToNode[index ? index.getX(t * 3 + c) : t * 3 + c]);
      for (const a of ids) for (const b of ids) if (a !== b) near[a].add(b);
    }
    // find a node from a position in the mesh's own space, allowing for the
    // float32 rounding three.js applied
    const lookup = (x, y, z) => {
      const bx = Math.round(x / q), by = Math.round(y / q), bz = Math.round(z / q);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const n = nodeOfKey.get((bx + dx) + ',' + (by + dy) + ',' + (bz + dz));
        if (n !== undefined) return n;
      }
      return -1;
    };
    return { world, near: near.map((s) => [...s]), vToNode, lookup };
  }

  function weightsFor(p, segs, m, box) {
    const d = V(), cp = V();
    const ranked = segs.map((s) => {
      const ab = d.copy(s.b).sub(s.a);
      const t = clamp(cp.copy(p).sub(s.a).dot(ab) / (s.len * s.len), 0, 1);
      const at = s.a.clone().addScaledVector(ab, t);
      return { s, t, at, dist: at.distanceTo(p) };
    }).sort((x, y) => x.dist - y.dist);
    // A hidden bone may give way only to one nearly as close. And sight only
    // means something from inside the mesh: an eyeball or a button has no
    // bone in it, so it simply takes the nearest.
    let pick = ranked[0];
    const reach = ranked[0].dist + S.H * 0.12;
    for (const c of ranked.slice(0, 6)) {
      if (c.dist > reach) break;
      if (c.dist < 1e-9 || !box.containsPoint(c.at)) { pick = c; break; }
      const dir = p.clone().sub(c.at).divideScalar(c.dist);
      vis.set(c.at, dir);
      vis.far = c.dist - Math.max(c.dist * 0.02, S.H * 0.002);
      if (vis.far <= 0 || !vis.intersectObject(m, false).length) { pick = c; break; }
    }
    const { s, t } = pick, w = {};
    let own = 1;
    if (s.up && t < BLEND_ZONE) { const b = 0.5 * smoothstep(1 - t / BLEND_ZONE); w[s.up] = b; own -= b; }
    if (s.down && t > 1 - BLEND_ZONE) { const c = 0.5 * smoothstep(1 - (1 - t) / BLEND_ZONE); w[s.down] = c; own -= c; }
    const st = s.stations;
    let k = st.length - 1;
    for (let i = 0; i < st.length - 1; i++) if (t < st[i + 1].t) { k = i; break; }
    const add = (key, v) => { w[key] = (w[key] || 0) + v; };
    if (k === st.length - 1) add(st[k].key, own);
    else {
      const f = (t - st[k].t) / (st[k + 1].t - st[k].t);
      add(st[k].key, own * (1 - f));
      add(st[k + 1].key, own * f);
    }
    return w;
  }

  function prune(w) {
    const top = Object.entries(w).filter(([, v]) => v >= 0.01).sort((a, b) => b[1] - a[1]).slice(0, MAX_INFLUENCES);
    const sum = top.reduce((n, [, v]) => n + v, 0) || 1;
    return Object.fromEntries(top.map(([k, v]) => [k, v / sum]));
  }

  function computeWeights() {
    const segs = boneSegments();
    const meshes = S.meshes.map((m) => {
      const g = weld(m);
      const box = new THREE.Box3().setFromObject(m, true);
      let W = g.world.map((p) => weightsFor(p, segs, m, box));
      for (let pass = 0; pass < SMOOTH_PASSES; pass++) {
        W = W.map((w, i) => {
          const out = {};
          for (const [k, v] of Object.entries(w)) out[k] = v * 0.5;
          const share = 0.5 / Math.max(g.near[i].length, 1);
          if (!g.near[i].length) for (const [k, v] of Object.entries(w)) out[k] += v * 0.5;
          for (const j of g.near[i]) for (const [k, v] of Object.entries(W[j])) out[k] = (out[k] || 0) + v * share;
          return out;
        });
      }
      return { mesh: m, g, box, W: W.map(prune) };
    });

    // line each mesh up with the file's own vertex list
    if (S.order) {
      for (const entry of meshes) {
        const pos = entry.mesh.geometry.attributes.position;
        let best = null;
        for (const src of S.order) {
          const n = src.positions.length / 3;
          const nodeOf = new Int32Array(n);
          let missed = 0;
          for (let i = 0; i < n; i++) {
            nodeOf[i] = entry.g.lookup(src.positions[i * 3], src.positions[i * 3 + 1], src.positions[i * 3 + 2]);
            if (nodeOf[i] < 0) missed++;
          }
          // every node of the mesh should be some file vertex, and nearly
          // every file vertex a node of this mesh
          if (missed <= n * 0.01 && n >= entry.g.world.length && (!best || missed < best.missed)) {
            best = { src, nodeOf, missed };
          }
        }
        if (best && pos.count) entry.file = best;
      }
    }
    S.weights = { meshes, segs };
  }

  // Influence colours for the preview: the block palette, by joint.
  const PALETTE = ['#FFE66D', '#4ECDC4', '#FF6B6B', '#BFD7EA', '#91AEC1', '#7DD181',
    '#A96DA3', '#EF8354', '#DF3B57', '#D8A47F', '#F0B3DE', '#5AB1BB'].map((c) => new THREE.Color(c));
  const jointColor = (key) => PALETTE[ALL_KEYS.indexOf(key) % PALETTE.length];
  const COLD = new THREE.Color('#2E2E34'), WARM = new THREE.Color('#FF6210'), HOT = new THREE.Color('#FFE66D');
  const weightMat = clay.clone();
  weightMat.vertexColors = true;
  weightMat.color.set(0xffffff);
  addWire(weightMat);

  // Paint the weights on the mesh: one joint as a heat map when it is the
  // selected point, every joint in its own colour otherwise.
  function paintWeights() {
    if (!S.weights) return;
    const focus = S.selected && S.joints[S.selected] && ALL_KEYS.includes(S.selected) ? S.selected : null;
    const c = new THREE.Color();
    for (const { mesh, g, W } of S.weights.meshes) {
      const pos = mesh.geometry.attributes.position;
      const colors = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) {
        const w = W[g.vToNode[i]];
        if (focus) {
          const v = w[focus] || 0;
          c.copy(COLD).lerp(WARM, Math.min(v * 2, 1));
          if (v > 0.5) c.lerp(HOT, (v - 0.5) * 2);
        } else {
          c.setRGB(0, 0, 0);
          for (const [k, v] of Object.entries(w)) c.r += jointColor(k).r * v, c.g += jointColor(k).g * v, c.b += jointColor(k).b * v;
        }
        colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
      }
      mesh.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    }
  }

  function showWeights(on) {
    const btn = $('[data-weights]');
    if (on && !S.weights) {
      busySkin('Calculating weights…');
      computeWeights();
    }
    btn.setAttribute('aria-pressed', String(!!on));
    if (on) paintWeights();
    for (const m of S.meshes) m.material = on ? weightMat : clay;
    skinStatus();
    invalidate();
  }

  function busySkin(text) {
    $('[data-skin-status]').textContent = text;
  }

  function skinStatus() {
    let text;
    if (!S.pivot) text = '';
    else if (!S.weights) text = 'Weights are calculated when you download, or press Weights to see them.';
    else {
      const out = S.weights.meshes.filter((e) => e.file).length;
      text = S.weights.meshes.length + (S.weights.meshes.length === 1 ? ' mesh' : ' meshes') + ' weighted, up to ' +
        MAX_INFLUENCES + ' joints per vertex.' +
        (S.order ? ' ' + out + ' of ' + S.weights.meshes.length + ' go in the skin pack.' : '');
    }
    if (S.pivot && S.skinNote) text += ' ' + S.skinNote;
    busySkin(text);
  }

  // One Mutant Tools jSkin per mesh, in IOSkin's compressed format: per
  // joint, the weight of each vertex by index, zeros left out.
  // `nameOf` turns a joint here into the influence name in the file; joints
  // that share a name add up.
  function jSkin(entry, nameOf = jointName) {
    const name = entry.file.src.name;
    const weights = {};
    const src = entry.file.src.positions, p = V();
    const eyes = S.eyeParts.has(entry.mesh) ? SIDES.filter((s) => S.joints[s + 'Eyes']) : [];
    const nearestEye = (q) => eyes.reduce((a, b) =>
      (q.distanceToSquared(S.joints[a + 'Eyes']) <= q.distanceToSquared(S.joints[b + 'Eyes']) ? a : b));
    entry.file.nodeOf.forEach((node, i) => {
      // an eyeball turns with its eye: all of it on the nearer eye's joint.
      // A file vertex three.js dropped (one no polygon uses) is weighted from
      // its own position, so nothing is left without a joint
      const w = eyes.length
        ? { [nearestEye(p.set(src[i * 3], src[i * 3 + 1], src[i * 3 + 2]).applyMatrix4(entry.mesh.matrixWorld)) + 'Eyes']: 1 }
        : node >= 0 ? entry.W[node] : prune(weightsFor(
          p.set(src[i * 3], src[i * 3 + 1], src[i * 3 + 2]).applyMatrix4(entry.mesh.matrixWorld).clone(),
          S.weights.segs, entry.mesh, entry.box));
      for (const [k, v] of Object.entries(w)) {
        const joint = weights[nameOf(k)] || (weights[nameOf(k)] = {});
        joint[i] = Math.round(((joint[i] || 0) + v) * 1e6) / 1e6;
      }
    });
    return {
      objs: [name],
      objDDic: [{
        weights,
        blendWeights: {},
        skinClsName: name + '_skinCluster',
        objName: name,
        nameSpace: '',
        vertexCount: entry.file.nodeOf.length,
        skinDataFormat: 'compressed',
        skinningMethod: 0,
        normalizeWeights: 1,
      }],
      bypassObj: [],
    };
  }

  // ------------------------------------------------------------- topology
  // The wireframe is drawn by the surface's own shader, so it bends with the
  // mesh while the rig plays. Each triangle carries which of its edges are
  // edges of the model's own polygons (a quad's diagonal is not), read from
  // the FBX; other formats show every triangle edge.
  const wire = { value: 0 };
  function addWire(material) {
    material.onBeforeCompile = (shader) => {
      shader.uniforms.wireOn = wire;
      shader.vertexShader = 'attribute vec3 wireBary;\nattribute vec3 wireMask;\nvarying vec3 vWireBary;\nvarying vec3 vWireMask;\n' +
        shader.vertexShader.replace('#include <begin_vertex>',
          '#include <begin_vertex>\nvWireBary = wireBary;\nvWireMask = wireMask;');
      shader.fragmentShader = 'uniform float wireOn;\nvarying vec3 vWireBary;\nvarying vec3 vWireMask;\n' +
        shader.fragmentShader.replace('#include <dithering_fragment>', [
          '#include <dithering_fragment>',
          'if (wireOn > 0.5) {',
          '  vec3 e = smoothstep(vec3(0.0), fwidth(vWireBary) * 1.3, vWireBary);',
          '  float line = 1.0;',
          '  if (vWireMask.x > 0.5) line = min(line, e.x);',
          '  if (vWireMask.y > 0.5) line = min(line, e.y);',
          '  if (vWireMask.z > 0.5) line = min(line, e.z);',
          '  gl_FragColor.rgb = mix(vec3(0.05), gl_FragColor.rgb, 0.25 + 0.75 * line);',
          '}',
        ].join('\n'));
    };
    material.customProgramCacheKey = () => 'mt-wire';
  }
  addWire(clay);

  // The polygon sizes of the FBX geometry this mesh came from, if the file
  // had them and the triangle count agrees.
  function polygonSizes(m, tris) {
    if (!S.order) return null;
    const count = (src) => src.sizes ? src.sizes.reduce((n, k) => n + k - 2, 0) : -1;
    const fits = S.order.filter((src) => count(src) === tris);
    return (fits.find((src) => src.name === m.name) || fits[0] || {}).sizes || null;
  }

  function wireAttributes(m) {
    const g = m.geometry;
    if (g.attributes.wireBary) return;
    const n = g.attributes.position.count, tris = n / 3;
    const bary = new Float32Array(n * 3), mask = new Float32Array(n * 3).fill(1);
    for (let i = 0; i < n; i++) bary[i * 3 + (i % 3)] = 1;
    const sizes = polygonSizes(m, tris);
    if (sizes) {
      // fan triangle (0, i - 1, i): the edge across from corner 0 is always
      // the polygon's own; the other two only at the fan's two ends
      let t = 0;
      for (const size of sizes) {
        for (let i = 2; i < size; i++, t++) {
          for (let k = 0; k < 3; k++) mask.set([1, i === size - 1 ? 1 : 0, i === 2 ? 1 : 0], (t * 3 + k) * 3);
        }
      }
    }
    g.setAttribute('wireBary', new THREE.BufferAttribute(bary, 3));
    g.setAttribute('wireMask', new THREE.BufferAttribute(mask, 3));
  }

  function showTopology(on) {
    if (on) S.meshes.forEach(wireAttributes);
    wire.value = on ? 1 : 0;
    invalidate();
  }

  // ------------------------------------------------------------ rig test
  // The placed skeleton, skinned with the computed weights and driven by
  // Quaternius' Universal Animation Library (CC0). Every joint copies the
  // turn of the matching bone, measured from that skeleton's own T-pose, so
  // the two rigs' joint orientations never have to agree. Forearm and shin
  // twist joints take a share of the wrist's and ankle's twist.
  const ANIM_URL = '/assets/models/quaternius-animations.glb';
  const RETARGET = { Spine_Root: 'pelvis', Spine_Base: 'spine_01', Spine_Belly: 'spine_02', Spine_Chest: 'spine_03',
    Neck: 'neck_01', Head: 'Head' };
  for (const P of SIDES) {
    const s = P === 'L_' ? 'l' : 'r';
    Object.assign(RETARGET, {
      [P + 'Clavicle']: 'clavicle_' + s, [P + 'Shoulder']: 'upperarm_' + s, [P + 'Elbow']: 'lowerarm_' + s,
      [P + 'Wrist']: 'hand_' + s, [P + 'Hip']: 'thigh_' + s, [P + 'Knee']: 'calf_' + s, [P + 'Ankle']: 'foot_' + s,
      [P + 'Foot_Ball']: 'ball_' + s,
    });
    for (const f of ['index', 'middle', 'ring', 'pinky']) {
      for (const n of ['01', '02', '03']) RETARGET[fingerKey(P, f, n)] = f + '_' + n + '_' + s;
    }
    ['00', '01', '02'].forEach((n, i) => { RETARGET[fingerKey(P, 'thumb', n)] = 'thumb_0' + (i + 1) + '_' + s; });
  }
  const test = { lib: null, rig: null, action: null, playing: false, last: 0 };
  const rigMat = new THREE.MeshStandardMaterial({ color: 0x9a968c, roughness: 0.85, metalness: 0, side: THREE.DoubleSide });
  addWire(rigMat);

  async function loadLibrary() {
    if (test.lib) return test.lib;
    const gltf = await new Promise((ok, fail) => new GLTFLoader().load(ANIM_URL, ok, undefined, fail));
    const nodes = {};
    gltf.scene.traverse((o) => { if (o.name) nodes[o.name] = o; });
    const mixer = new THREE.AnimationMixer(gltf.scene);
    // their T-pose: the pose every turn is measured from
    const tpose = gltf.animations.find((c) => c.name === 'A_TPose');
    if (tpose) { mixer.clipAction(tpose).play(); mixer.update(0); }
    gltf.scene.updateMatrixWorld(true);
    const ref = {};
    for (const name of Object.values(RETARGET)) {
      if (nodes[name]) ref[name] = nodes[name].getWorldQuaternion(new THREE.Quaternion());
    }
    const pelvis = nodes.pelvis.getWorldPosition(V());
    const floor = Math.min(nodes.ball_l.getWorldPosition(V()).y, nodes.foot_l.getWorldPosition(V()).y);
    // their character faces +Z with its left on +X, as here; if not, turn it
    const facing = new THREE.Quaternion();
    if (nodes.hand_l.getWorldPosition(V()).x < pelvis.x) facing.setFromAxisAngle(V(0, 1, 0), Math.PI);
    mixer.stopAllAction();
    test.lib = { scene: gltf.scene, nodes, ref, pelvis, height: pelvis.y - floor, facing, mixer,
      clips: Object.fromEntries(gltf.animations.map((c) => [c.name, c])) };
    return test.lib;
  }

  function buildRig() {
    if (!S.weights) computeWeights();
    S.meshes.forEach(wireAttributes);
    const bones = {}, order = [];
    for (const [key, parent] of S.list) {
      const b = new THREE.Bone();
      b.name = key;
      b.position.copy(parent ? S.joints[key].clone().sub(S.joints[parent]) : S.joints[key]);
      if (parent) bones[parent].add(b);
      bones[key] = b;
      order.push(key);
    }
    const group = new THREE.Group();
    group.add(bones[order[0]]);
    group.updateMatrixWorld(true);
    const skel = new THREE.Skeleton(order.map((k) => bones[k]));
    const index = Object.fromEntries(order.map((k, i) => [k, i]));
    const v = V();
    for (const { mesh, g, W } of S.weights.meshes) {
      const geo = mesh.geometry.clone();
      const n = geo.attributes.position.count;
      // the mesh as it stands, in the scene's own space, so the bind is plain
      const pos = geo.attributes.position;
      for (let i = 0; i < n; i++) pos.setXYZ(i, ...mesh.getVertexPosition(i, v).applyMatrix4(mesh.matrixWorld).toArray());
      if (geo.attributes.normal) geo.attributes.normal.applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld));
      const si = new Uint16Array(n * 4), sw = new Float32Array(n * 4);
      for (let i = 0; i < n; i++) {
        Object.entries(W[g.vToNode[i]]).slice(0, 4).forEach(([k, w], j) => { si[i * 4 + j] = index[k]; sw[i * 4 + j] = w; });
      }
      geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4));
      geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
      const sm = new THREE.SkinnedMesh(geo, rigMat);
      sm.frustumCulled = false;
      group.add(sm);
      sm.bind(skel, new THREE.Matrix4());
    }
    const rootY = S.joints.Spine_Root.y - S.bounds.min.y;
    return { group, bones, order, skel, rootBind: S.joints.Spine_Root.clone(), scale: rootY / test.lib.height };
  }

  // The part of a turn about one axis.
  function twistAbout(q, axis) {
    const p = axis.clone().multiplyScalar(axis.x * q.x + axis.y * q.y + axis.z * q.z);
    return new THREE.Quaternion(p.x, p.y, p.z, q.w).normalize();
  }

  function poseRig(dt) {
    const L = test.lib, R = test.rig;
    L.mixer.update(dt);
    L.scene.updateMatrixWorld(true);
    const world = {}, F = L.facing, Fi = F.clone().invert();
    for (const key of R.order) {
      const bone = R.bones[key], parent = bone.parent.isBone ? bone.parent.name : null;
      const theirs = RETARGET[key];
      let w;
      if (theirs && L.nodes[theirs] && L.ref[theirs]) {
        const delta = L.nodes[theirs].getWorldQuaternion(new THREE.Quaternion()).multiply(L.ref[theirs].clone().invert());
        w = F.clone().multiply(delta).multiply(Fi);
      } else {
        w = parent ? world[parent].clone() : new THREE.Quaternion();
      }
      world[key] = w;
      bone.quaternion.copy(parent ? world[parent].clone().invert().multiply(w) : w);
    }
    // forearm and shin twists: a share of the wrist's and ankle's turn about the bone
    for (const P of SIDES) {
      for (const [from, to] of [['Elbow', 'Wrist'], ['Knee', 'Ankle']]) {
        const axis = S.joints[P + to].clone().sub(S.joints[P + from]).normalize();
        const twist = twistAbout(R.bones[P + to].quaternion, axis);
        for (let i = 1; i <= S.twists; i++) {
          const b = R.bones[twistKey(P, from, i)];
          if (b) b.quaternion.identity().slerp(twist, i / (S.twists + 1));
        }
      }
    }
    // the root follows the pelvis, scaled to this body
    const move = L.nodes.pelvis.getWorldPosition(V()).sub(L.pelvis).applyQuaternion(F).multiplyScalar(R.scale);
    R.bones.Spine_Root.position.copy(R.rootBind).add(move);
  }

  function tick(now) {
    if (!test.playing) return;
    const dt = test.last ? Math.min((now - test.last) / 1000, 0.1) : 0;
    test.last = now;
    poseRig(dt);
    renderer.render(scene, S.view === '3d' ? persp : ortho);
    requestAnimationFrame(tick);
  }

  async function playTest(name) {
    stopTest();
    if (!name || !S.pivot) return;
    busySkin('Loading the animations…');
    try {
      await loadLibrary();
    } catch (err) {
      console.error(err);
      busySkin('The animations did not load.');
      return;
    }
    busySkin('Calculating weights…');
    await new Promise((ok) => setTimeout(ok, 30));
    test.rig = buildRig();
    scene.add(test.rig.group);
    S.pivot.visible = false;
    skeleton.visible = false;
    root.classList.add('is-testing');
    test.action = test.lib.mixer.clipAction(test.lib.clips[name]).reset().play();
    test.playing = true;
    test.last = 0;
    if (S.view !== '3d') setView('3d');
    skinStatus();
    requestAnimationFrame(tick);
  }

  // Stop the rig test. `clearPicker` when the skeleton or the model changed
  // under it, so the picker does not claim a test is still running.
  function stopTest(clearPicker = false) {
    test.playing = false;
    if (test.action) { test.action.stop(); test.action = null; }
    if (test.rig) {
      scene.remove(test.rig.group);
      test.rig.group.traverse((o) => o.geometry && o.geometry.dispose());
      test.rig = null;
    }
    root.classList.remove('is-testing');
    if (S.pivot) {
      S.pivot.visible = true;
      skeleton.visible = $('[data-bones]').getAttribute('aria-pressed') === 'true';
    }
    if (clearPicker) $('[data-anim]').value = '';
    invalidate();
  }

  // ------------------------------------------------------------- export
  const r4 = (n) => Math.round(n * 1e4) / 1e4 + 0; // + 0 turns -0 into 0
  // Joints go out as the page shows them: Y up, the character facing front
  // (+Z). Maya's FBX import may stand the file up turned another way; the
  // download's anchors let WebToRig move the character back onto them.
  function toFile() {
    const scale = Number($('[data-scale]').value) || 1;
    return (p) => p.clone().multiplyScalar(scale).toArray().map(r4);
  }

  // The scale list, with the file's own factor added when it is not one of
  // the usual ones.
  function setScale(scale) {
    const select = $('[data-scale]');
    const value = String(scale);
    if (![...select.options].some((o) => o.value === value)) {
      select.add(new Option('×' + value + ' · from the file', value));
    }
    select.value = value;
  }

  const jointName = (key) => key + '_Jnt';
  function rows() {
    const place = toFile();
    return S.list.map(([key, parent]) => ({
      key,
      name: jointName(key),
      parent: parent ? jointName(parent) : null,
      side: sideOf(key) ? sideOf(key)[0] : 'C',
      position: place(S.joints[key]),
    }));
  }

  // Every body guide of the template, by its name in the template, including
  // the ones that share a joint's position (Spine_End, L_ClavicleEnd ...), and
  // the foot pivots and eyes that are not joints at all.
  function guides() {
    const place = toFile();
    const out = {};
    const add = (name, key) => { if (S.joints[key]) out[name + '_Guide'] = place(S.joints[key]); };
    // twist joints are the skin's, not the template's: its limb block makes its own
    for (const [key] of S.list) if (!/Hand_End$/.test(key) && !isTwist(key)) add(key, key);
    for (const [alias, key] of Object.entries(GUIDE_ALIASES)) {
      if (alias === 'Spine_End') add(alias, key);
      else for (const s of SIDES) add(s + alias, s + key);
    }
    for (const s of SIDES) for (const g of FOOT_GUIDES) add(s + g, s + g);
    // each eye, and where it looks: straight ahead
    for (const s of SIDES) {
      const eye = S.joints[s + 'Eyes'];
      if (!eye) continue;
      add(s + 'Eyes', s + 'Eyes');
      out[s + 'Eyes_Aim_Guide'] = place(eye.clone().add(V(0, 0, S.H * EYE_AIM)));
    }
    return out;
  }

  function skeletonFile() {
    const place = toFile();
    const markers = {};
    for (const pt of POINTS) {
      if (pt.kind !== 'marker') continue;
      if (pt.finger && !FINGER_SETS[S.fingers].includes(pt.finger)) continue;
      markers[pt.id] = place(S.pos[pt.id]);
    }
    return JSON.stringify({
      format: FORMAT,
      version: FORMAT_VERSION,
      template: TEMPLATE,
      source: { tool: 'Mutant Tools Web to Rig', url: 'https://mutanttools.com/web-to-rig/', model: S.name },
      units: { scale: Number($('[data-scale]').value) },
      upAxis: 'y',
      sourceUpAxis: S.up,
      fingers: S.fingers,
      guides: guides(),
      joints: rows(),
      markers,
    }, null, 2) + '\n';
  }

  // ------------------------------------------------------------- manny
  // The skeleton that goes to Maya and carries the skin is Unreal's Manny
  // (SKM_Manny_BaseSkeleton, as captured in Mutant Tools'
  // Utils/Unreal/mannequin_skeleton_capture.json): its names, hierarchy and
  // joint orientations, moved onto this character. Each joint keeps Manny's
  // own orientation, swung only as far as its bone now points elsewhere, so
  // its axis conventions survive: X down the chain on the left arm and back up
  // it on the right, the left leg's X toward its parent, and so on.
  const MANNY_URL = '/assets/models/manny-reference.json';
  const DROP_IN_URL = '/assets/maya/Drag_into_Maya.py';
  let mannyRef = null;
  const loadManny = async () => mannyRef || (mannyRef = await (await fetch(MANNY_URL)).json());

  // Where each Manny joint goes, from the joints placed here: one joint, or a
  // point between two.
  const MANNY_FROM = {
    pelvis: 'Spine_Root', spine_01: 'Spine_Base', spine_02: 'Spine_Belly', spine_03: ['Spine_Belly', 'Spine_Chest'],
    spine_04: 'Spine_Chest', spine_05: ['Spine_Chest', 'Neck'], neck_01: 'Neck', neck_02: ['Neck', 'Head'], head: 'Head',
  };
  // The child each Manny joint aims down. Joints without one turn with their parent.
  const MANNY_AIM = {
    pelvis: 'spine_01', spine_01: 'spine_02', spine_02: 'spine_03', spine_03: 'spine_04', spine_04: 'spine_05',
    spine_05: 'neck_01', neck_01: 'neck_02', neck_02: 'head',
  };
  // The joints here whose skin each Manny joint takes. Cups and the leg's
  // pelvis joint have no Manny twin and give theirs to the hand and pelvis;
  // twists go by where they sit along the bone. The eyes have no Manny twin
  // either: they get joints of their own under the head (see mannyFile).
  const MANNY_SKIN = {
    Spine_Root: 'pelvis', Spine_Base: 'spine_01', Spine_Belly: 'spine_02', Spine_Chest: 'spine_04', Neck: 'neck_01',
    Head: 'head',
  };
  for (const P of SIDES) {
    const s = P === 'L_' ? '_l' : '_r';
    Object.assign(MANNY_FROM, {
      ['clavicle' + s]: P + 'Clavicle', ['upperarm' + s]: P + 'Shoulder', ['lowerarm' + s]: P + 'Elbow',
      ['hand' + s]: P + 'Wrist', ['thigh' + s]: P + 'Hip', ['calf' + s]: P + 'Knee', ['foot' + s]: P + 'Ankle',
      ['ball' + s]: P + 'Foot_Ball',
    });
    Object.assign(MANNY_AIM, {
      ['clavicle' + s]: 'upperarm' + s, ['upperarm' + s]: 'lowerarm' + s, ['lowerarm' + s]: 'hand' + s,
      ['hand' + s]: 'middle_metacarpal' + s, ['thigh' + s]: 'calf' + s, ['calf' + s]: 'foot' + s, ['foot' + s]: 'ball' + s,
      ['thumb_01' + s]: 'thumb_02' + s, ['thumb_02' + s]: 'thumb_03' + s,
    });
    Object.assign(MANNY_SKIN, {
      [P + 'Clavicle']: 'clavicle' + s, [P + 'Shoulder']: 'upperarm' + s, [P + 'Elbow']: 'lowerarm' + s,
      [P + 'Wrist']: 'hand' + s, [P + 'Hand_InnerCup']: 'hand' + s, [P + 'Hand_OutterCup']: 'hand' + s,
      [P + 'Hand_End']: 'hand' + s, [P + 'Pelvis']: 'pelvis', [P + 'Hip']: 'thigh' + s, [P + 'Knee']: 'calf' + s,
      [P + 'Ankle']: 'foot' + s, [P + 'Foot_Ball']: 'ball' + s, [P + 'Eyes']: 'eye' + s,
      [twistKey(P, 'Shoulder', 1)]: 'upperarm_twist_01' + s, [twistKey(P, 'Shoulder', 2)]: 'upperarm_twist_02' + s,
      [twistKey(P, 'Elbow', 1)]: 'lowerarm_twist_02' + s, [twistKey(P, 'Elbow', 2)]: 'lowerarm_twist_01' + s,
      [twistKey(P, 'Hip', 1)]: 'thigh_twist_01' + s, [twistKey(P, 'Hip', 2)]: 'thigh_twist_01' + s,
      [twistKey(P, 'Knee', 1)]: 'calf_twist_02' + s, [twistKey(P, 'Knee', 2)]: 'calf_twist_01' + s,
    });
    for (const f of ['index', 'middle', 'ring', 'pinky']) {
      const meta = f + '_metacarpal' + s;
      MANNY_FROM[meta] = fingerKey(P, f, '00');
      MANNY_AIM[meta] = f + '_01' + s;
      MANNY_SKIN[fingerKey(P, f, '00')] = meta;
      for (const n of ['01', '02', '03']) {
        MANNY_FROM[f + '_' + n + s] = fingerKey(P, f, n);
        MANNY_SKIN[fingerKey(P, f, n)] = f + '_' + n + s;
      }
      MANNY_AIM[f + '_01' + s] = f + '_02' + s;
      MANNY_AIM[f + '_02' + s] = f + '_03' + s;
    }
    ['00', '01', '02'].forEach((n, i) => {
      MANNY_FROM['thumb_0' + (i + 1) + s] = fingerKey(P, 'thumb', n);
      MANNY_SKIN[fingerKey(P, 'thumb', n)] = 'thumb_0' + (i + 1) + s;
    });
  }

  // Manny moved onto this character: each joint's world position and
  // rotation, in the export's space (Y-up, centimetres).
  function fitManny(ref) {
    const place = toFile();
    const at = (key) => V(...place(S.joints[key]));
    const refT = (k) => V(...ref.joints[k].t);
    const refQ = (k) => new THREE.Quaternion().setFromEuler(
      new THREE.Euler(...ref.joints[k].r.map((a) => THREE.MathUtils.degToRad(a)), 'ZYX'));
    const T = {}, R = {}, swing = {};

    for (const k of ref.order) {
      const src = MANNY_FROM[k];
      if (Array.isArray(src)) T[k] = at(src[0]).lerp(at(src[1]), 0.5);
      else if (src && S.joints[src]) T[k] = at(src);
    }
    T.root = V(T.pelvis.x, place(V(0, S.bounds.min.y, 0))[1], T.pelvis.z);
    for (const k of ref.order) {
      if (T[k]) continue;
      const side = k.slice(-2);
      const twist = k.match(/^(upperarm|lowerarm|thigh|calf)_twist_\d+_[lr]$/);
      if (twist) {
        // a twist sits where Manny has it along its bone
        const bone = twist[1] + side, next = MANNY_AIM[bone];
        const ab = refT(next).sub(refT(bone));
        T[k] = T[bone].clone().lerp(T[next], refT(k).sub(refT(bone)).dot(ab) / ab.lengthSq());
      } else if (/^(attach|ik_foot_root|ik_hand_root)$/.test(k)) {
        T[k] = T.root.clone();
      } else if (/^ik_foot_[lr]$/.test(k)) {
        T[k] = T['foot' + side].clone();
      } else if (/^ik_hand_[lr]$/.test(k)) {
        T[k] = T['hand' + side].clone();
      } else if (k === 'ik_hand_gun') {
        T[k] = T.hand_r.clone();
      }
    }

    for (const k of ref.order) {
      const parent = ref.joints[k].parent, aim = MANNY_AIM[k];
      if (/^(root|attach|ik_)/.test(k)) swing[k] = new THREE.Quaternion();
      else if (aim && T[aim] && T[k]) {
        const a = refT(aim).sub(refT(k)), b = T[aim].clone().sub(T[k]);
        swing[k] = a.lengthSq() > 1e-8 && b.lengthSq() > 1e-8
          ? new THREE.Quaternion().setFromUnitVectors(a.normalize(), b.normalize())
          : (swing[parent] || new THREE.Quaternion()).clone();
      } else {
        swing[k] = (swing[parent] || new THREE.Quaternion()).clone();
      }
      // a finger this character does not have folds into the hand
      if (!T[k]) T[k] = (T[parent] || T.root).clone();
      if (/^weapon_[lr]$/.test(k)) {
        T[k] = T[parent].clone().add(refT(k).sub(refT(parent)).applyQuaternion(swing[parent]));
      }
      R[k] = swing[k].clone().multiply(refQ(k));
    }
    return { T, R };
  }

  // The fitted skeleton in the capture's own format, so Mutant Tools'
  // mannequin_utils.recreate_mannequin_from_json builds it as it stands. Each
  // joint's rotation goes in its joint orient; rotate stays zero, ready to bind.
  function mannyFile(ref) {
    const { T, R } = fitManny(ref);
    const deg = (q) => new THREE.Euler().setFromQuaternion(q, 'ZYX').toArray().slice(0, 3)
      .map((a) => r4(THREE.MathUtils.radToDeg(a)));
    const order = [...ref.order];
    const parent = Object.fromEntries(order.map((k) => [k, ref.joints[k].parent]));
    const radius = Object.fromEntries(order.map((k) => [k, ref.joints[k].radius]));
    // Manny has no eyes: each one gets a joint under the head, turned like the
    // head, where its handle is, to carry the eyeball's skin
    const place = toFile();
    for (const s of SIDES) {
      const k = MANNY_SKIN[s + 'Eyes'];
      if (!S.joints[s + 'Eyes']) continue;
      T[k] = V(...place(S.joints[s + 'Eyes']));
      R[k] = R.head.clone();
      parent[k] = 'head';
      radius[k] = radius.head * 0.5;
      order.push(k);
    }
    const joints = {};
    for (const k of order) {
      const p = parent[k];
      const pq = p ? R[p] : new THREE.Quaternion(), pt = p ? T[p] : V();
      const pqi = pq.clone().invert();
      joints[k] = {
        parent: p,
        world_translate: T[k].toArray().map(r4),
        world_rotate: deg(R[k]),
        local_translate: T[k].clone().sub(pt).applyQuaternion(pqi).toArray().map(r4),
        local_rotate: [0, 0, 0],
        local_scale: [1, 1, 1],
        joint_orient: deg(pqi.multiply(R[k])),
        rotate_order: 0,
        radius: radius[k],
        segment_scale_compensate: false,
      };
    }
    return {
      meta: { version: 1, description: 'Manny (SKM_Manny_BaseSkeleton) fitted to ' + S.name + ' by Mutant Tools Web to Rig' },
      joint_order: order,
      joints,
    };
  }

  const readme = () => [
    'Web to Rig (Mutant Tools): ' + S.name,
    'https://mutanttools.com/web-to-rig/',
    '',
    'Drag Drag_into_Maya.py onto the viewport in Maya 2022 or newer. It installs',
    'Mutant Tools if you do not have it, then walks you through:',
    '  1. importing ' + S.source.name + ' on a Manny skeleton with its skin,',
    '  2. placing the HumanUnrealGameTemplate guides, to check,',
    '  3. building the rig and driving the Manny joints with it.',
    'Its Extra tab tries the rig with Mutant Tools\' Mixamo animations.',
    '',
    'Files:',
    '  ' + S.source.name + '   your character, unchanged',
    '  manny_skeleton.json   Unreal\'s Manny skeleton fitted to it, plus eye joints (Y-up, cm)',
    '  skeleton.json         the template guides and the placed joints',
    '  skin/                 Mutant Tools skin pack for the Manny joints',
    '  web_to_rig.json       how the files fit together',
    '',
  ].join('\n');

  // Everything Maya needs, in one folder inside the zip.
  async function bundle() {
    if (!S.weights) computeWeights();
    const ref = await loadManny();
    const dropIn = await (await fetch(DROP_IN_URL)).text();
    const dir = slug() + '_mutant_tools/';
    const files = {
      [dir + 'Drag_into_Maya.py']: strToU8(dropIn),
      [dir + 'README.txt']: strToU8(readme()),
      [dir + 'skeleton.json']: strToU8(skeletonFile()),
      [dir + 'manny_skeleton.json']: strToU8(JSON.stringify(mannyFile(ref), null, 1) + '\n'),
      [dir + S.source.name]: S.source.bytes,
    };
    const packed = S.weights.meshes.filter((e) => e.file);
    const names = [];
    for (const entry of packed) {
      const fileName = entry.file.src.name.replace(/[|:]/g, '_') + '.jSkin';
      names.push(fileName);
      files[dir + 'skin/' + fileName] = strToU8(JSON.stringify(jSkin(entry, (k) => MANNY_SKIN[k] || 'pelvis'), null, 1) + '\n');
    }
    const pack = 'skin/' + slug() + '.bSkinPack';
    if (names.length) files[dir + pack] = strToU8(JSON.stringify({ packFiles: names, rootPath: '' }, null, 4) + '\n');
    files[dir + 'web_to_rig.json'] = strToU8(JSON.stringify({
      format: 'mutant-tools-web-to-rig',
      version: 1,
      model: S.name,
      mesh: S.source.name,
      meshes: packed.map((e) => e.file.src.name),
      skeleton: 'skeleton.json',
      manny: 'manny_skeleton.json',
      skin_pack: names.length ? pack : null,
      template: TEMPLATE,
      units: 'cm',
      up_axis: 'y',
      fingers: S.fingers,
      anchors: anchors(packed),
      site: 'https://mutanttools.com/web-to-rig/',
    }, null, 2) + '\n');
    skinStatus();
    return zipSync(files, { level: 6 });
  }

  // Where a few of each mesh's own vertices are, numbered as in the file and
  // placed as the skeleton is: the extremes along each axis and some between.
  function anchors(packed) {
    const place = toFile(), out = {};
    for (const { file, g } of packed) {
      const { src, nodeOf } = file, n = nodeOf.length, picks = new Set();
      const at = (i, k) => g.world[nodeOf[i]].getComponent(k);
      for (let k = 0; k < 3; k++) {
        let lo = -1, hi = -1;
        for (let i = 0; i < n; i++) {
          if (nodeOf[i] < 0) continue;
          if (lo < 0 || at(i, k) < at(lo, k)) lo = i;
          if (hi < 0 || at(i, k) > at(hi, k)) hi = i;
        }
        if (lo >= 0) picks.add(lo).add(hi);
      }
      for (let i = 0; i < n; i += Math.max(1, Math.floor(n / 12))) if (nodeOf[i] >= 0) picks.add(i);
      out[src.name] = { vertices: n, points: [...picks].map((i) => [i, ...place(g.world[nodeOf[i]])]) };
    }
    return out;
  }

  function download(name, data, type) {
    const url = URL.createObjectURL(new Blob([data], { type }));
    const a = Object.assign(document.createElement('a'), { href: url, download: name });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const slug = () => S.name.replace(/[^\w-]+/g, '_');
  $('[data-dl-zip]').addEventListener('click', async () => {
    busySkin('Packing the files for Maya…');
    // let the status paint before the work starts
    await new Promise((ok) => setTimeout(ok, 30));
    try {
      download(slug() + '_mutant_tools.zip', await bundle(), 'application/zip');
    } catch (err) {
      console.error(err);
      busySkin('The download could not be made. Try again.');
    }
  });
  $('[data-dl-json]').addEventListener('click', () => download(slug() + '_skeleton.json', skeletonFile(), 'application/json'));

  $('[data-count]').textContent = S.list.length + ' joints';
  setView('front');

  // ?debug in the address exposes the internals to the console, for tuning
  // the auto placement against a character's own skeleton
  if (new URLSearchParams(location.search).has('debug')) {
    window.__placer = { S, autoPlace, loadBuffer, rebuild, movePoint, guessFingers };
  }
}

// The control points of every mesh in a binary FBX, in the file's order: the
// vertex order Maya gives each mesh on import, which a skin file indexes by.
// Returns { meshes: [{ name, positions }], upAxis, unitScale }, each mesh
// named after its model, or null for a text FBX. upAxis (1 = Y, 2 = Z) and
// unitScale (centimetres per file unit) are what Maya converts by on import.
// Only what that needs is decoded; other arrays are skipped.
function readFbxMeshes(buffer) {
  const u8 = new Uint8Array(buffer), dv = new DataView(buffer);
  const latin = new TextDecoder('latin1');
  if (latin.decode(u8.subarray(0, 18)) !== 'Kaydara FBX Binary') return null;
  const big = dv.getUint32(23, true) >= 7500;
  let off = 27;
  const word = () => {
    const v = big ? Number(dv.getBigUint64(off, true)) : dv.getUint32(off, true);
    off += big ? 8 : 4;
    return v;
  };
  function prop(keepArray) {
    const t = String.fromCharCode(u8[off++]);
    let v = null;
    switch (t) {
      case 'Y': off += 2; break;
      case 'C': v = u8[off]; off += 1; break;
      case 'I': v = dv.getInt32(off, true); off += 4; break;
      case 'F': off += 4; break;
      case 'D': v = dv.getFloat64(off, true); off += 8; break;
      case 'L': v = dv.getBigInt64(off, true).toString(); off += 8; break;
      case 'S': case 'R': {
        const n = dv.getUint32(off, true);
        off += 4;
        if (t === 'S') v = latin.decode(u8.subarray(off, off + n));
        off += n;
        break;
      }
      default: { // f d l i b: an array, maybe deflated
        const n = dv.getUint32(off, true), enc = dv.getUint32(off + 4, true), len = dv.getUint32(off + 8, true);
        off += 12;
        if (keepArray && (t === 'd' || t === 'i')) {
          let raw = u8.subarray(off, off + len);
          if (enc) raw = unzlibSync(raw);
          v = t === 'd' ? new Float64Array(raw.slice().buffer, 0, n) : new Int32Array(raw.slice().buffer, 0, n);
        }
        off += len;
      }
    }
    return v;
  }
  function node() {
    const end = word(), count = word();
    word();
    const nameLen = u8[off++];
    const name = latin.decode(u8.subarray(off, off + nameLen));
    off += nameLen;
    if (end === 0) return null;
    const props = [];
    for (let i = 0; i < count; i++) props.push(prop(name === 'Vertices' || name === 'PolygonVertexIndex'));
    const kids = [];
    while (off < end) {
      const k = node();
      if (!k) break;
      kids.push(k);
    }
    off = end;
    return { name, props, kids };
  }
  const top = {};
  while (off < u8.length - 160) {
    const n = node();
    if (!n) break;
    top[n.name] = n;
  }
  if (!top.Objects || !top.Connections) return null;
  const settings = {};
  const globals = top.GlobalSettings && top.GlobalSettings.kids.find((k) => k.name === 'Properties70');
  for (const p of globals ? globals.kids : []) settings[p.props[0]] = p.props[4];
  const clean = (s) => (s || '').split('\x00\x01')[0];
  const geometry = {}, models = {};
  for (const o of top.Objects.kids) {
    if (o.name === 'Geometry' && o.props[2] === 'Mesh') {
      const verts = o.kids.find((k) => k.name === 'Vertices');
      const poly = o.kids.find((k) => k.name === 'PolygonVertexIndex');
      // each polygon's corner count: its last index is stored as -(index + 1)
      const sizes = [];
      if (poly && poly.props[0]) {
        let n = 0;
        for (const v of poly.props[0]) { n++; if (v < 0) { sizes.push(n); n = 0; } }
      }
      if (verts && verts.props[0]) geometry[o.props[0]] = { positions: verts.props[0], sizes };
    } else if (o.name === 'Model') {
      models[o.props[0]] = clean(o.props[1]);
    }
  }
  const out = [];
  for (const c of top.Connections.kids) {
    if (c.props[0] === 'OO' && geometry[c.props[1]] && models[c.props[2]] !== undefined) {
      out.push({ name: models[c.props[2]], ...geometry[c.props[1]] });
    }
  }
  return { meshes: out, upAxis: settings.UpAxis ?? 1, unitScale: settings.UnitScaleFactor || 1 };
}

// An OBJ's vertices in "v" order, the order Maya keeps for a single object.
function readObjVertices(text, fileName) {
  const v = [];
  let objects = 0, name = '';
  for (const line of text.split('\n')) {
    if (line.startsWith('v ')) {
      const [, x, y, z] = line.trim().split(/\s+/);
      v.push(+x, +y, +z);
    } else if (/^o\s/.test(line)) {
      objects++;
      name = name || line.slice(2).trim();
    }
  }
  return { name: name || fileName.replace(/\.[^.]+$/, ''), positions: Float64Array.from(v), objects };
}
