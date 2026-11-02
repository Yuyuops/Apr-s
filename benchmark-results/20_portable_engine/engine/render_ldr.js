// Headless renderer for brickify .ldr models: real LDraw part geometry (from ldr_expand.py scene JSON),
// three.js WebGL in Chromium (Playwright). No image post-processing, no generative model.
// usage: node render_ldr.js scene.json views.json outdir
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, sceneFile, viewsFile, outDir] = process.argv;
const THREE_DIR = path.join(__dirname, 'node_modules', 'three');
const PAGE = `<!doctype html><html><head><style>html,body{margin:0;background:#fff}</style>
<script type="importmap">{"imports":{"three":"http://local/three/build/three.module.js","three/addons/":"http://local/three/examples/jsm/"}}</script>
</head><body><script type="module">
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
window.ready = (async () => {
  const IS_GLB = __ISGLB__; const GLB_NATIVE = __GLBNATIVE__;
  const S = IS_GLB ? {meshes:{}, parts:[], colours:{}} : await (await fetch('http://local/scene.json')).json();
  const dec = b => { const s = atob(b); const u = new Uint8Array(s.length); for (let i=0;i<s.length;i++) u[i]=s.charCodeAt(i); return new Float32Array(u.buffer); };
  const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#ffffff');
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(renderer), 0.04).texture;
  const root = new THREE.Group(); root.scale.set(0.4, -0.4, -0.4); scene.add(root);  // LDU->mm, LDraw(-Y up)->Y up
  const geos = {};
  for (const [k, m] of Object.entries(S.meshes)) {
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(dec(m.tris), 3));
    const gn = g.toNonIndexed(); gn.computeVertexNormals();
    const e = new THREE.BufferGeometry(); e.setAttribute('position', new THREE.BufferAttribute(dec(m.edges), 3));
    geos[k] = {g: gn, e};
  }
  const items = S.parts.map((p, i) => {
    const m = new THREE.Matrix4(); const M = p.M;
    m.set(M[0],M[1],M[2],p.o[0], M[3],M[4],M[5],p.o[1], M[6],M[7],M[8],p.o[2], 0,0,0,1);
    return {...p, mat: m, layer: (p.y0 !== undefined ? p.y0 : Math.round(-p.o[1]/8)), i};
  });
  const maxLayer = items.length ? Math.max(...items.map(p => p.layer)) : 0;
  const lights = new THREE.Group(); scene.add(lights);
  lights.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 1.1));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); lights.add(sun); lights.add(sun.target);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShadowMaterial({opacity: 0.18}));
  ground.rotation.x = -Math.PI/2; ground.receiveShadow = true; scene.add(ground);
  let built = null, glbScene = null;
  if (IS_GLB) {
    glbScene = (await new GLTFLoader().loadAsync('http://local/scene.json')).scene;
    glbScene.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    root.scale.set(1, 1, 1);
    // normalise like brickify: height (Y extent) -> v.heightMm, base on y=0
    if (!GLB_NATIVE) {   // default: scale a GLB to 250 mm height; GLB_NATIVE=1 keeps its own mm coordinates (comparison frames)
    const b = new THREE.Box3().setFromObject(glbScene); const s = 250 / (b.max.y - b.min.y);
    glbScene.scale.setScalar(s); glbScene.position.set(-s*(b.min.x+b.max.x)/2, -s*b.min.y, -s*(b.min.z+b.max.z)/2); }
  }
  function build(v) {
    if (IS_GLB) { if (!built) { built = new THREE.Group(); built.add(glbScene); root.add(built); } return; }
    if (built) { root.remove(built); built.traverse(o => { if (o.material) o.material.dispose(); }); }
    built = new THREE.Group(); root.add(built);
    const sel = items.filter(p => (v.maxLayer == null || p.layer <= v.maxLayer));
    const groups = {};
    for (const p of sel) {
      const old = v.maxLayer != null && v.ghostOld && p.layer < v.maxLayer;
      const key = p.p + '|' + p.c + '|' + (old ? 1 : 0);
      (groups[key] = groups[key] || []).push(p);
    }
    const sec = v.explodeEvery || 12, gap = v.explode || 0;
    for (const [key, ps] of Object.entries(groups)) {
      const [pk, c, old] = key.split('|');
      const col = S.colours[c] || {hex:'#888888', edge:'#333333', alpha:1};
      let base = new THREE.Color(col.hex);
      if (old === '1') base.lerp(new THREE.Color('#ffffff'), 0.55);
      const mat = new THREE.MeshStandardMaterial({color: base, roughness: 0.32, metalness: 0.0,
        transparent: col.alpha < 1, opacity: col.alpha, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1, side: THREE.DoubleSide});
      const im = new THREE.InstancedMesh(geos[pk].g, mat, ps.length); im.castShadow = true; im.receiveShadow = true;
      const lineMat = new THREE.LineBasicMaterial({color: old === '1' ? '#9aa3ab' : (c === '0' ? '#595959' : '#1b1b1b'), transparent: true, opacity: v.edges === false ? 0 : 0.55});
      ps.forEach((p, j) => {
        const m = p.mat.clone();
        if (gap) { const s = Math.floor(p.layer / sec); m.premultiply(new THREE.Matrix4().makeTranslation(0, -s * gap / 0.4, 0)); }
        im.setMatrixAt(j, m);
        if (v.edges !== false) { const ls = new THREE.LineSegments(geos[pk].e, lineMat); ls.matrixAutoUpdate = false; ls.matrix.copy(m); built.add(ls); }
      });
      built.add(im);
    }
  }
  window.renderView = (v) => {
    build(v);
    renderer.setSize(v.w || 1400, v.h || 1400, false); renderer.setPixelRatio(1);
    scene.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(built); const c = box.getCenter(new THREE.Vector3()); const sz = box.getSize(new THREE.Vector3());
    const fullBox = v.frameBox ? new THREE.Box3(new THREE.Vector3(...v.frameBox[0]), new THREE.Vector3(...v.frameBox[1])) : box;
    const fc = fullBox.getCenter(new THREE.Vector3()), fs = fullBox.getSize(new THREE.Vector3());
    const r = 0.5 * fs.length();
    const az = (v.az || 0) * Math.PI / 180, el = (v.el || 0) * Math.PI / 180, fov = 24;
    const cam = new THREE.PerspectiveCamera(fov, (v.w||1400)/(v.h||1400), 1, 100000);
    const d = r / Math.sin(fov * Math.PI / 360) * (v.zoom || 1.0);
    cam.position.set(fc.x + d * Math.cos(el) * Math.sin(az), fc.y + d * Math.sin(el), fc.z + d * Math.cos(el) * Math.cos(az));
    cam.lookAt(fc);
    sun.position.set(fc.x + r * 2 * Math.sin(az + 0.6), fc.y + r * 3, fc.z + r * 2 * Math.cos(az + 0.6)); sun.target.position.copy(fc);
    const sc = sun.shadow.camera; sc.left = -r*1.5; sc.right = r*1.5; sc.top = r*1.5; sc.bottom = -r*1.5; sc.near = 1; sc.far = r * 10; sc.updateProjectionMatrix();
    ground.position.set(fc.x, box.min.y - 0.01, fc.z); ground.scale.set(r * 8, r * 8, 1);
    renderer.render(scene, cam);
    return {png: renderer.domElement.toDataURL('image/png'), bbox_mm: [box.min.toArray(), box.max.toArray()], maxLayer};
  };
  return {maxLayer, nParts: items.length};
})();
</script></body></html>`;
(async () => {
  const views = JSON.parse(fs.readFileSync(viewsFile, 'utf8'));
  fs.mkdirSync(outDir, {recursive: true});
  const browser = await chromium.launch({args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const page = await browser.newPage();
  page.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
  page.on('pageerror', e => console.error('pageerror:', e.message));
  await page.route('http://local/**', async route => {
    const u = new URL(route.request().url()).pathname;
    if (u === '/') return route.fulfill({body: PAGE.replace('__ISGLB__', sceneFile.endsWith('.glb') ? 'true' : 'false').replace('__GLBNATIVE__', process.env.GLB_NATIVE ? 'true' : 'false'), contentType: 'text/html'});
    if (u === '/scene.json') return route.fulfill({path: sceneFile, contentType: sceneFile.endsWith('.glb') ? 'model/gltf-binary' : 'application/json'});
    if (u.startsWith('/three/')) return route.fulfill({path: path.join(THREE_DIR, u.slice(7)), contentType: 'text/javascript'});
    route.fulfill({status: 404});
  });
  await page.goto('http://local/');
  const info = await page.evaluate(() => window.ready);
  console.log('scene', JSON.stringify(info));
  const meta = {};
  for (const v of views) {
    const t = Date.now();
    const r = await page.evaluate(v => window.renderView(v), v);
    fs.writeFileSync(path.join(outDir, v.name + '.png'), Buffer.from(r.png.split(',')[1], 'base64'));
    meta[v.name] = {view: v, bbox_mm: r.bbox_mm};
    console.log(v.name, ((Date.now() - t) / 1000).toFixed(1) + 's');
  }
  fs.writeFileSync(path.join(outDir, 'render_meta.json'), JSON.stringify({scene: info, views: meta}, null, 1));
  await browser.close();
})();
