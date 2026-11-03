"""Self-contained zoomable / rotatable HTML viewer (three.js inlined). Boxes + cylinder studs at the real LDraw dimensions ; real LEGO colour values ; click a part to identify it ; layer slider, section and region filters."""
import base64, json, os
from .render import NODE_MODULES
from .common import rb_colours

def three_assets():
    d = os.path.join(NODE_MODULES, "three"); r = lambda p: open(os.path.join(d, p), "rb").read(); return r("build/three.module.min.js"), r("examples/jsm/controls/OrbitControls.js")

JS = r"""
import * as THREE from 'three'; import { OrbitControls } from 'orbit';
const D = JSON.parse(document.getElementById('data').textContent); const P = D.parts; const S = 20, HP = 8, N = D.N, cx = N * S / 2;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#f2f1ee');
const cam = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 1, 6000); const rend = new THREE.WebGLRenderer({antialias: true}); rend.setSize(innerWidth, innerHeight); rend.setPixelRatio(devicePixelRatio); document.body.appendChild(rend.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.95)); const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(300, 900, 400); scene.add(sun);
const box = new THREE.BoxGeometry(1, 1, 1), stud = new THREE.CylinderGeometry(6, 6, 4, 18); const mats = {};
const m = (c) => mats[c] || (mats[c] = new THREE.MeshStandardMaterial({color: new THREE.Color(c), roughness: 0.4, metalness: 0}));
const lineMat = new THREE.LineBasicMaterial({color: 0x222222, transparent: true, opacity: 0.4}); const group = new THREE.Group(); scene.add(group); const picks = [];
P.forEach((p) => {
  const g = new THREE.Group(), h = p.h * HP;
  const b = new THREE.Mesh(box, m(p.rgb)); b.scale.set(p.d * S, h, p.w * S); b.position.set(0, h / 2, 0); b.userData = p; g.add(b); picks.push(b);
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(box), lineMat); e.scale.copy(b.scale); e.position.copy(b.position); g.add(e);
  if (p.studs) for (let a = 0; a < p.d; a++) for (let c = 0; c < p.w; c++) { const s = new THREE.Mesh(stud, m(p.rgb)); s.position.set((a + 0.5 - p.d / 2) * S, h + 2, (c + 0.5 - p.w / 2) * S); g.add(s); }
  g.position.set((p.z + p.d / 2) * S - cx, p.zbot * HP, (p.x + p.w / 2) * S - cx); p._g = g; p._b = b; group.add(g);
});
const home = () => { cam.up.set(0, 1, 0); cam.position.set(0, N * S * 0.95, N * S * 0.8); ctl.target.set(0, 20, 0); ctl.update(); };
const ctl = new OrbitControls(cam, rend.domElement); home();
const $ = (i) => document.getElementById(i); const sl = $('layer'); sl.max = D.maxLevel; sl.value = D.maxLevel; let sel = null;
const secOn = {dos: true, relief: true, cadre: true}; let regSel = '';
function vis() { const k = +sl.value; $('lab').textContent = k >= D.maxLevel ? 'toutes les couches' : k + ' plaque(s) de hauteur sur ' + D.maxLevel; P.forEach(p => { p._g.visible = (p.zbot + p.h) <= k && secOn[p.section] && (!regSel || p.region === regSel); }); }
sl.oninput = vis; ['dos', 'relief', 'cadre'].forEach(s => { $('s_' + s).onchange = (e) => { secOn[s] = e.target.checked; vis(); }; });
const rs = $('reg'); [''].concat(D.regions).forEach(r => { const o = document.createElement('option'); o.value = r; o.textContent = r || 'toutes les regions'; rs.appendChild(o); }); rs.onchange = () => { regSel = rs.value; vis(); };
$('persp').onclick = home; $('top').onclick = () => { cam.up.set(0, 0, -1); cam.position.set(0, N * S * 2.1, 0); ctl.target.set(0, 0, 0); ctl.update(); }; $('side').onclick = () => { cam.up.set(0, 1, 0); cam.position.set(N * S * 1.4, 40, 0); ctl.target.set(0, 20, 0); ctl.update(); };
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2(); const tip = $('tip'), info = $('info'); let down = null;
function pick(ev) { mouse.set(ev.clientX / innerWidth * 2 - 1, -ev.clientY / innerHeight * 2 + 1); ray.setFromCamera(mouse, cam); const h = ray.intersectObjects(picks.filter(x => x.parent.visible))[0]; return h ? h.object.userData : null; }
const desc = (p) => '<b>' + p.part + '</b> ' + p.size + ' ' + p.kind + '<br>couleur : ' + p.colour_name + ' (' + p.colour + ')<br>section : ' + p.section + ' / ' + p.layer + '<br>region : ' + p.region + '<br>id #' + p.id + ' - colonne ' + p.z + ', ligne ' + p.x;
rend.domElement.addEventListener('pointermove', ev => { const p = pick(ev); if (p) { tip.style.display = 'block'; tip.style.left = ev.clientX + 12 + 'px'; tip.style.top = ev.clientY + 12 + 'px'; tip.textContent = p.part + ' ' + p.size + ' - ' + p.colour_name + ' - ' + p.region; } else tip.style.display = 'none'; });
rend.domElement.addEventListener('pointerdown', ev => { down = [ev.clientX, ev.clientY]; });
rend.domElement.addEventListener('pointerup', ev => { if (!down || Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) > 4) return; const p = pick(ev); if (sel) { sel._b.material = m(sel.rgb); sel = null; } if (p) { sel = p; p._b.material = new THREE.MeshStandardMaterial({color: new THREE.Color(p.rgb), emissive: 0xffaa00, emissiveIntensity: 0.55}); info.innerHTML = desc(p); } else info.innerHTML = 'Cliquer une piece pour l\'identifier.'; });
addEventListener('resize', () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); rend.setSize(innerWidth, innerHeight); });
vis(); (function loop() { requestAnimationFrame(loop); ctl.update(); rend.render(scene, cam); })(); window.__ready = true; window.__pickFirst = () => { const p = P[Math.floor(P.length / 2)]; info.innerHTML = desc(p); return p.part; };
"""

def write_viewer(model, out, title):
    rb = rb_colours(); P = []
    for p in model["parts"]:
        sec = {"B": "dos", "L": "relief", "F": "cadre"}[p["layer"][0]]
        P.append(dict(id=p["id"], x=p["x"], z=p["z"], w=p["w"], d=p["d"], zbot=p["zbot"], h=p["h"], kind=p["kind"], studs=p["kind"] != "tile" and p["part"] != "98138", layer=p["layer"], section=sec, region=p["region"], part=p["part"], size=p["size"], colour=p["colour"], colour_name=rb[p["colour"]]["name"], rgb="#%02x%02x%02x" % tuple(rb[p["colour"]]["rgb"])))
    three, orbit = three_assets(); b64 = lambda b: "data:text/javascript;base64," + base64.b64encode(b).decode()
    maxl = max(p["zbot"] + p["h"] for p in model["parts"]); regions = sorted({p["region"] for p in model["parts"] if p["region"] not in ("dos", "cadre")})
    html = ("<!doctype html><html lang='fr'><head><meta charset='utf-8'><title>%s</title><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<style>html,body{margin:0;overflow:hidden;font:13px system-ui,sans-serif;background:#f2f1ee}#ui{position:fixed;top:8px;left:8px;background:#fffd;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px #0003;max-width:420px}#info{position:fixed;right:8px;top:8px;background:#fffd;padding:8px 10px;border-radius:8px;min-width:210px;box-shadow:0 1px 4px #0003}#tip{position:fixed;display:none;background:#222;color:#fff;padding:3px 7px;border-radius:4px;font-size:12px;pointer-events:none}button{margin-right:4px}</style>"
            "<script type='importmap'>{\"imports\":{\"three\":\"%s\",\"orbit\":\"%s\"}}</script></head><body>"
            "<div id='ui'><b>%s</b><br><button id='persp'>3/4</button><button id='top'>Dessus</button><button id='side'>Profil</button><br><label>couches <input id='layer' type='range' min='1' value='1'></label> <span id='lab'></span><br>"
            "<label><input type='checkbox' id='s_dos' checked> dos</label> <label><input type='checkbox' id='s_relief' checked> relief</label> <label><input type='checkbox' id='s_cadre' checked> cadre</label> <select id='reg'></select><br>"
            "<small>Glisser = tourner, molette = zoom, clic droit = deplacer, <b>clic sur une piece = reference</b>. Couleurs reelles LEGO ; geometrie simplifiee (boite + tenons aux cotes LDraw), rendus fideles dans renders/.</small></div><div id='info'>Cliquer une piece pour l'identifier.</div><div id='tip'></div>"
            "<script id='data' type='application/json'>%s</script><script type='module'>%s</script></body></html>"
            ) % (title, b64(three), b64(orbit), title, json.dumps(dict(parts=P, N=model["N"], maxLevel=maxl, regions=regions)), JS)
    open(out, "w", encoding="utf-8").write(html); return len(html)
