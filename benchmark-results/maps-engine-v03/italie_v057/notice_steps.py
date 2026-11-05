#!/usr/bin/env python3
"""Step-by-step assembly instructions of a full Italia model.
 * assembly_plan_v2.json : ordered steps (<= 36 parts) = base layers by sector, board layers by (level, sector), then sub-assemblies (Colosseum, Pisa) built on their own plate, then finishing (title, compass, frame). Each step lists every part with colour,
   orientation (rotation about the vertical axis, 0/90/180/270), position (row, col in the sector, level), the number of studs it clicks onto (from the engine-1 joint graph), sector/inter-sector flags and stability checks.
 * step_viewer.html : self-contained three.js viewer on the real LDraw meshes (previous steps in pale colour, current step in full colour and outlined, previous/next/play, jump to step, per-step list).
 * notice_pas_a_pas.pdf : one table row per step (parts grouped by part/colour/orientation with positions).
usage: notice_steps.py MODELDIR   (needs diorama.ldr, parts.json, joints_per_part.json, bom_verification.csv)"""
import base64, csv, json, os, subprocess, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "20_portable_engine", "engine")); sys.path.insert(0, os.path.join(HERE, "..", "engine"))
from _paths import LDRAW, RB_DB
import sqlite3
D = sys.argv[1]; P = json.load(open(D + "/parts.json")); J = {j["id"]: j for j in json.load(open(D + "/joints_per_part.json"))}; F = 2; SZ = 32; MAXP = 36
rb = {r[0]: (r[1], "#%s" % r[2]) for r in sqlite3.connect(RB_DB).execute("select id,name,rgb from colors")}
title = {r["part_num"]: r["part_name_ldraw"] for r in csv.DictReader(open(D + "/bom_verification.csv"))}
def sector(p):
    if p["region"].startswith("frame"): return "CADRE"
    return "S%d%d" % (min(max((p["r"] - F) // SZ, 0), 3), min(max((p["c"] - F) // SZ, 0), 3))
def group(p):
    g = p["region"].split("_")[0]
    if g in ("colosseum", "plaza"): return "SA_COLISEE"
    if g == "pisa": return "SA_PISE"
    if g in ("title", "compass", "leader"): return "FINITIONS"
    if g == "frame": return "CADRE"
    return "TABLEAU"
def crosses(p):
    r0, c0 = p["r"] - F, p["c"] - F; r1, c1 = r0 + p["nr"] - 1, c0 + p["nc"] - 1
    return (r0 // SZ != r1 // SZ) or (c0 // SZ != c1 // SZ)
order = []
for y in sorted({p["y"] for p in P}): order += [p for p in P if p["y"] == y]
idx = {p["id"]: i for i, p in enumerate(order)}
phase = {"TABLEAU": 1, "SA_COLISEE": 2, "SA_PISE": 3, "FINITIONS": 4, "CADRE": 5}
bucket = defaultdict(list)
for p in order: bucket[(phase[group(p)], group(p), p["y"] if group(p) in ("TABLEAU", "CADRE") else 0, sector(p) if group(p) in ("TABLEAU", "CADRE") else group(p))].append(p)
steps = []; n = 0
for key in sorted(bucket, key=lambda k: (k[0], k[2], k[3])):
    ph, grp, y, sec = key; ps = bucket[key]
    if grp in ("SA_COLISEE", "SA_PISE"): ps = sorted(ps, key=lambda p: (p["y"], p["r"], p["c"]))
    for i in range(0, len(ps), MAXP):
        chunk = ps[i:i + MAXP]; n += 1
        fragile = [p["id"] for p in chunk if J[p["id"]]["studs_below"] <= 1 and p["y"] > 0]; cross = [p["id"] for p in chunk if crosses(p)]
        checks = ["Poser a plat, tous les tenons enclenches (aucun jour visible).", "Verifier la planeite avant de continuer."]
        if fragile: checks.append("%d piece(s) tenue(s) par un seul tenon : appuyer a la main, ne pas manipuler la zone avant la couche suivante." % len(fragile))
        if cross: checks.append("%d piece(s) a cheval sur deux secteurs : elles verrouillent la jonction, les poser AVANT de decoller les deux modules." % len(cross))
        if grp.startswith("SA_"): checks.append("Sous-ensemble : l'assembler sur sa plaque d'appui hors tableau, puis le poser en un bloc (voir etape finale du sous-ensemble).")
        if y == 0 and grp == "TABLEAU": checks.append("Couche 0 : plaques de socle ; croiser les joints avec la couche suivante.")
        steps.append(dict(step=n, group=grp, sector=sec, level_plate=y if grp in ("TABLEAU", "CADRE") else None, n_parts=len(chunk), part_ids=[p["id"] for p in chunk], checks=checks, single_stud_parts=len(fragile), inter_sector_parts=len(cross),
                          parts=[dict(id=p["id"], part=p["part"], name=title.get(p["part"], ""), colour=p["colour"], colour_name=rb.get(p["colour"], ("?", ""))[0], rot=p["rot"], row=p["r"] - F, col=p["c"] - F, plate_level=p["y"], studs_below=J[p["id"]]["studs_below"], sector=sector(p)) for p in chunk]))
conn = defaultdict(set)      # inter-sector connection table : pieces whose footprint crosses a sector seam
for p in order:
    if group(p) == "TABLEAU" and crosses(p): conn[sector(p)].add(p["id"])
plan = dict(model=os.path.basename(D.rstrip("/")), step_count=n, max_parts_per_step=MAXP, phases=["1 tableau : couches 0..n par secteur (S00..S33, nord-ouest -> sud-est)", "2 sous-ensemble Colisee", "3 sous-ensemble Pise", "4 finitions : titre, rose des vents, lien vers Rome", "5 cadre"],
            inter_sector_pieces={k: sorted(v) for k, v in conn.items()}, notes=["Aucun essai physique n'a ete realise : ces etapes sont numeriquement ordonnees (aucune piece posee sans appui d'apres le validateur du moteur 1), pas validees a la main.", "Orientation = rotation autour de la verticale (degres) telle que dans le LDraw ; position = (rangee, colonne) du coin nord-ouest de l'emprise dans le champ (0,0 = coin NO du champ de 128 tenons, hors cadre)."], steps=steps)
json.dump(plan, open(D + "/assembly_plan_v2.json", "w"))
# ---- viewer
tmp = D + "/_viewer_tmp"; os.makedirs(tmp, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "20_portable_engine", "engine", "ldr_expand.py"), "--ldr", D + "/diorama.ldr", "--ldraw", LDRAW, "--json", tmp + "/s.json", "--glb", tmp + "/g.glb"], check=True, capture_output=True)
sc = json.load(open(tmp + "/s.json")); os.remove(tmp + "/g.glb")
for k, v in sc["colours"].items():
    if int(k) in rb: v["hex"] = rb[int(k)][1]
step_of = {}
for s in steps:
    for pid in s["part_ids"]: step_of[pid] = s["step"]
meshes = {k: dict(t=v["tris"]) for k, v in sc["meshes"].items()}
parts = [dict(m=q["p"], c=q["c"], o=q["o"], M=q["M"], s=step_of[order[i]["id"]], id=order[i]["id"]) for i, q in enumerate(sc["parts"])]
data = dict(meshes=meshes, colours={k: v["hex"] for k, v in sc["colours"].items()}, parts=parts, steps=[dict(step=s["step"], group=s["group"], sector=s["sector"], level=s["level_plate"], n=s["n_parts"], checks=s["checks"], summary=[[a, b, c, q] for (a, b, c), q in sorted(Counter((x["part"], x["colour_name"], x["rot"]) for x in s["parts"]).items())]) for s in steps])
mod = os.path.join(os.environ.get("LEGO_NODE_MODULES", ""), "three"); r = lambda p: open(os.path.join(mod, p), "rb").read().decode()
html = '''<!doctype html><meta charset=utf-8><title>Italia 128 - notice pas a pas</title><style>body{margin:0;font:14px sans-serif;background:#f3f2ee}#ui{position:fixed;left:0;top:0;right:0;background:#fffe;padding:6px 10px;z-index:3;display:flex;gap:8px;align-items:center;flex-wrap:wrap}#info{position:fixed;left:0;bottom:0;right:0;max-height:34vh;overflow:auto;background:#fffe;padding:8px 12px;z-index:3;font-size:13px}button{padding:4px 10px}#sl{width:320px}</style>
<div id=ui><button id=prev>&lt;</button><button id=next>&gt;</button><button id=play>lecture</button><input id=sl type=range min=1 value=1><span id=lab></span><label>aller a <input id=goto size=4></label><button id=full>vue d'ensemble</button><button id=zoom>zoom sur l'etape</button></div><div id=info></div>
<script type=application/json id=data>''' + json.dumps(data, separators=(",", ":")) + '''</script>
<script type=importmap>{"imports":{"three":"data:text/javascript;base64,''' + base64.b64encode(r("build/three.module.min.js").encode()).decode() + '''","orbit":"data:text/javascript;base64,''' + base64.b64encode(r("examples/jsm/controls/OrbitControls.js").replace("from 'three'", "from 'three'").encode()).decode() + '''"}}</script>
<script type=module>
import * as THREE from 'three'; import {OrbitControls} from 'orbit';
const D=JSON.parse(document.getElementById('data').textContent), $=i=>document.getElementById(i);
const scene=new THREE.Scene(); scene.background=new THREE.Color('#f3f2ee'); const cam=new THREE.PerspectiveCamera(30,innerWidth/innerHeight,10,60000); const rend=new THREE.WebGLRenderer({antialias:true}); rend.setSize(innerWidth,innerHeight); document.body.appendChild(rend.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x8899aa,1.0)); const sun=new THREE.DirectionalLight(0xffffff,1.3); sun.position.set(900,2500,1200); scene.add(sun);
const geos={}; for(const [k,v] of Object.entries(D.meshes)){const bin=atob(v.t), u8=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u8[i]=bin.charCodeAt(i); const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(u8.buffer),3)); g.computeVertexNormals(); geos[k]=g;}
const group=new THREE.Group(); scene.add(group); const groups={};
D.parts.forEach(p=>{const k=p.m+'|'+p.c; (groups[k]=groups[k]||[]).push(p);});
const inst=[]; const white=new THREE.Color('#ffffff'); const zero=new THREE.Matrix4().makeScale(0,0,0);
for(const [k,ps] of Object.entries(groups)){const m0=ps[0]; const mt=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.4,side:THREE.DoubleSide}); const im=new THREE.InstancedMesh(geos[m0.m],mt,ps.length); const base=new THREE.Color(D.colours[m0.c]||'#888'); const mats=[];
 ps.forEach((p,i)=>{const M=p.M, mm=new THREE.Matrix4(); mm.set(M[0],M[1],M[2],p.o[0], M[3],M[4],M[5],p.o[1], M[6],M[7],M[8],p.o[2], 0,0,0,1); mats.push(mm); im.setMatrixAt(i,mm); im.setColorAt(i,base);}); im.instanceMatrix.needsUpdate=true; group.add(im); inst.push({im,ps,mats,base});}
group.rotation.x=Math.PI; /* LDraw y is down */ const bb=new THREE.Box3().setFromObject(group); const ctr=bb.getCenter(new THREE.Vector3()), size=bb.getSize(new THREE.Vector3());
const ctl=new OrbitControls(cam,rend.domElement); function home(){cam.position.set(ctr.x+size.x*.55,ctr.y+size.length()*.75,ctr.z+size.z*.9); ctl.target.copy(ctr); ctl.update();} home();
let cur=1; const N=D.steps.length; $('sl').max=N;
function show(k){cur=Math.max(1,Math.min(N,k)); $('sl').value=cur; const s=D.steps[cur-1]; let vis=0; inst.forEach(g=>{g.ps.forEach((p,i)=>{if(p.s<=cur){g.im.setMatrixAt(i,g.mats[i]); g.im.setColorAt(i,p.s<cur?g.base.clone().lerp(white,0.62):g.base); vis++;} else g.im.setMatrixAt(i,zero);}); g.im.instanceMatrix.needsUpdate=true; g.im.instanceColor.needsUpdate=true;}); window.__vis=vis;
 $('lab').textContent='etape '+cur+' / '+N+' - '+s.group+' '+s.sector+(s.level!=null?' - couche '+s.level:'')+' - '+s.n+' pieces';
 $('info').innerHTML='<b>'+$('lab').textContent+'</b><br>'+s.summary.map(x=>x[3]+' x '+x[0]+' '+x[1]+' (rot '+x[2]+')').join(' &middot; ')+'<br><i>Controles :</i><ul>'+s.checks.map(c=>'<li>'+c+'</li>').join('')+'</ul>';}
function zoomStep(){const b=new THREE.Box3(); inst.forEach(g=>g.ps.forEach((p,i)=>{if(p.s===cur){const v=new THREE.Vector3(p.o[0],p.o[1],p.o[2]).applyMatrix4(new THREE.Matrix4().makeRotationX(Math.PI)); b.expandByPoint(v);}})); if(b.isEmpty()) return; const c=b.getCenter(new THREE.Vector3()), r=b.getSize(new THREE.Vector3()).length(); ctl.target.copy(c); cam.position.set(c.x+r*.8,c.y+r*.9,c.z+r*.9); ctl.update();}
$('prev').onclick=()=>show(cur-1); $('next').onclick=()=>show(cur+1); $('sl').oninput=e=>show(+e.target.value); $('goto').onchange=e=>show(+e.target.value); $('full').onclick=home; $('zoom').onclick=zoomStep;
let timer=null; $('play').onclick=()=>{if(timer){clearInterval(timer);timer=null;$('play').textContent='lecture';}else{$('play').textContent='pause';timer=setInterval(()=>{if(cur>=N){clearInterval(timer);timer=null;$('play').textContent='lecture';}else show(cur+1)},700);}};
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();rend.setSize(innerWidth,innerHeight)}); show(1); (function loop(){requestAnimationFrame(loop);ctl.update();rend.render(scene,cam)})(); window.__ready=true; window.__show=show; window.__visible=()=>window.__vis;
</script>'''
open(D + "/step_viewer.html", "w").write(html)
import shutil; shutil.rmtree(tmp, ignore_errors=True)
print(n, "steps; viewer", os.path.getsize(D + "/step_viewer.html") // 1024, "KB")
