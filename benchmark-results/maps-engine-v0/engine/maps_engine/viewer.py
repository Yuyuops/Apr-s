"""Self-contained zoomable / rotatable HTML viewer (three.js inlined). Geometry = box + cylinder studs at real LDraw dimensions (the faithful renders in renders/ use the full LDraw part geometry)."""
import base64, json, os
import palette_util as PU
from .render import NODE_MODULES
from .build import y_top

def three_assets():
    d = os.path.join(NODE_MODULES, "three"); r = lambda p: open(os.path.join(d, p), "rb").read()
    return r("build/three.module.min.js"), r("examples/jsm/controls/OrbitControls.js")

JS = r"""
import * as THREE from 'three'; import { OrbitControls } from 'orbit';
const D = JSON.parse(document.getElementById('data').textContent); const P = D.parts;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#f4f4f2');
const cam = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 1, 5000); const rend = new THREE.WebGLRenderer({antialias: true}); rend.setSize(innerWidth, innerHeight); rend.setPixelRatio(devicePixelRatio); document.body.appendChild(rend.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.7)); const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(300, 800, 200); scene.add(sun);
const S = 20, H = 8, N = D.n; const cx = N * S / 2;
const box = new THREE.BoxGeometry(1, 1, 1); const stud = new THREE.CylinderGeometry(6, 6, 4, 18);
const mats = {}; const m = (c) => mats[c] || (mats[c] = new THREE.MeshStandardMaterial({color: new THREE.Color(c), roughness: 0.35}));
const group = new THREE.Group(); scene.add(group); const meshes = [];
const lineMat = new THREE.LineBasicMaterial({color: 0x333333, transparent: true, opacity: 0.45});
P.forEach((p) => {
  const g = new THREE.Group();
  const b = new THREE.Mesh(box, m(p.rgb)); b.scale.set(p.d * S, H, p.w * S); b.position.set(0, H / 2, 0); b.userData = p; g.add(b); meshes.push(b);
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(box), lineMat); e.scale.copy(b.scale); e.position.copy(b.position); g.add(e);
  for (let a = 0; a < p.d; a++) for (let c = 0; c < p.w; c++) { const s = new THREE.Mesh(stud, m(p.rgb)); s.position.set((a + 0.5 - p.d / 2) * S, H + 2, (c + 0.5 - p.w / 2) * S); g.add(s); }
  g.position.set((p.z + p.d / 2) * S - cx, p.y, (p.x + p.w / 2) * S - cx);   /* x = image column, z = image row (south = +z, toward the default camera) */ p._g = g; group.add(g);
});
cam.position.set(0, N * S * 0.95, N * S * 0.8); const ctl = new OrbitControls(cam, rend.domElement); ctl.target.set(0, 20, 0); ctl.update();
const ui = document.getElementById('ui'); const tip = document.getElementById('tip'); const maxL = D.levels;
const sl = document.getElementById('layer'); sl.max = maxL; sl.value = maxL; const lab = document.getElementById('lab');
sl.oninput = () => { const k = +sl.value; P.forEach(p => p._g.visible = (p.level + 3) <= k); lab.textContent = k >= maxL ? 'toutes les couches' : (k + ' couche(s) sur ' + maxL); };
document.getElementById('top').onclick = () => { cam.up.set(0, 0, -1); cam.position.set(0, N * S * 2.1, 0); ctl.target.set(0, 0, 0); ctl.update(); };
document.getElementById('persp').onclick = () => { cam.up.set(0, 1, 0); cam.position.set(0, N * S * 0.95, N * S * 0.8); ctl.target.set(0, 20, 0); ctl.update(); };
document.getElementById('side').onclick = () => { cam.up.set(0, 1, 0); cam.position.set(N * S * 1.3, 40, 0); ctl.target.set(0, 20, 0); ctl.update(); };
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
rend.domElement.addEventListener('pointermove', ev => { mouse.set(ev.clientX / innerWidth * 2 - 1, -ev.clientY / innerHeight * 2 + 1); ray.setFromCamera(mouse, cam); const h = ray.intersectObjects(meshes.filter(x => x.parent.visible))[0]; if (h) { const p = h.object.userData; tip.style.display = 'block'; tip.style.left = ev.clientX + 12 + 'px'; tip.style.top = ev.clientY + 12 + 'px'; tip.textContent = p.part + ' ' + p.size + ' - ' + p.colour_name + ' - region: ' + p.region + ' - couche ' + p.layer + ' - id ' + p.id; } else tip.style.display = 'none'; });
addEventListener('resize', () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); rend.setSize(innerWidth, innerHeight); });
sl.oninput(); (function loop() { requestAnimationFrame(loop); ctl.update(); rend.render(scene, cam); })();
window.__ready = true;
"""

def write_viewer(model, out, title):
    codes = PU.codes(); P = []
    for p in model["parts"]:
        c = codes[p["colour"]][1]
        P.append(dict(id=p["id"], x=p["x"], z=p["z"], w=p["w"], d=p["d"], y=-y_top(p) - 8, level=p["level"], layer=p["layer"], region=p["region"], part=p["part"], size=p["name_size"], colour_name=codes[p["colour"]][0], rgb="#%02x%02x%02x" % tuple(c)))
    three, orbit = three_assets()
    b64 = lambda b: "data:text/javascript;base64," + base64.b64encode(b).decode()
    html = ("<!doctype html><html lang='fr'><head><meta charset='utf-8'><title>%s</title><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<style>html,body{margin:0;overflow:hidden;font:14px system-ui,sans-serif;background:#f4f4f2}#ui{position:fixed;top:8px;left:8px;background:#fffc;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px #0003}#tip{position:fixed;display:none;background:#222;color:#fff;padding:3px 7px;border-radius:4px;font-size:12px;pointer-events:none}button{margin-right:4px}</style>"
            "<script type='importmap'>{\"imports\":{\"three\":\"%s\",\"orbit\":\"%s\"}}</script></head><body>"
            "<div id='ui'><b>%s</b><br><button id='persp'>3/4 (sud)</button><button id='top'>Dessus (nord en haut)</button><button id='side'>Profil (est)</button> <label>couches <input id='layer' type='range' min='1' value='1'></label> <span id='lab'></span><br><small>Glisser = tourner, molette = zoom, clic droit = deplacer, survol = piece. Geometrie simplifiee (boite + tenons aux cotes LDraw) ; rendus fideles : dossier renders/.</small></div><div id='tip'></div>"
            "<script id='data' type='application/json'>%s</script><script type='module'>%s</script></body></html>"
            ) % (title, b64(three), b64(orbit).replace("from 'three'", "from 'three'"), title, json.dumps(dict(parts=P, n=model["n"], levels=model["levels"] + 2)), JS)
    open(out, "w", encoding="utf-8").write(html); return len(html)
