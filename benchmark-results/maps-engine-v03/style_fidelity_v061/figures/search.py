#!/usr/bin/env python3
"""Figure SEARCH (no invention) : looks up EXISTING, catalogued LEGO minifigures in the Rebrickable catalogue snapshot (rb.db, local) for a theme, and records for each :
 exact catalogue name, catalogue id (fig-xxxxxx), parts count, real image (downloaded from the catalogue's own image URL), the sets that contain it (set number, name, year), the page link (standard Rebrickable URL pattern),
 availability = 'non verifie', price = null.  BrickLink and the official LEGO catalogue are NOT consulted : they are blocked from this environment (HTTP 405 / 403, checked at run time) -> reported as such, no data copied from memory.
 Nothing is generated or designed : if no catalogued figure matches, the answer is 'Aucune figurine verifiee'.
 usage : search.py THEME [--no-images]   (themes/THEME.json)  ->  results/THEME_candidates.json"""
import json, os, re, sqlite3, sys, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "20_portable_engine", "engine"))
from _paths import RB_DB
def probe(url):
    try: return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lego-maps-research"}), timeout=15).status
    except urllib.error.HTTPError as e: return e.code
    except Exception as e: return "error:%s" % type(e).__name__
def search(theme, images=True):
    cfg = json.load(open(os.path.join(HERE, "themes", theme + ".json"))); db = sqlite3.connect(RB_DB); snap = db.execute("select value from rb_db_lov").fetchall()
    found = {}
    def add(fig, reason, rel, note=None):
        f = found.setdefault(fig[0], dict(fig_num=fig[0], name=fig[1], parts=fig[2], image_url=fig[3], sets=[], match=[], relevance=rel))
        f["match"].append(reason); f["relevance"] = "strong" if "strong" in (rel, f["relevance"]) else rel
        if note: f["note"] = note
    sets_all = db.execute("select set_num,name,year,theme_id from sets").fetchall(); themes = {t[0]: t for t in db.execute("select id,name,parent_id from themes")}
    def theme_chain(tid):
        out = []
        while tid is not None and tid in themes: out.append(themes[tid][1]); tid = themes[tid][2]
        return out
    matched_sets = {}
    for sn, name, year, tid in sets_all:
        strong = any(re.search(p, name) for p in cfg.get("set_name_regex", [])); ind = any(re.search(p, name) for p in cfg.get("indirect_set_name_regex", []))
        th = any(re.search(p, t) for p in cfg.get("theme_name_regex", []) for t in theme_chain(tid))
        if strong or th: matched_sets[sn] = (name, "strong", "set %s : %s" % (sn, name) if strong else "catalogue theme '%s' : set %s (%s)" % ("/".join(theme_chain(tid)), sn, name))
        elif ind: matched_sets[sn] = (name, "indirect", "set %s : %s (city/landmark word in the set name only)" % (sn, name))
    for sn, (name, rel, why) in matched_sets.items():
        for fig in db.execute("select m.fig_num,m.name,m.num_parts,m.img_url from inventory_minifigs im join inventories i on i.id=im.inventory_id join minifigs m on m.fig_num=im.fig_num where i.set_num=?", (sn,)): add(fig, why, rel, "relevance by set name only : judge the cultural fit on the photo" if rel == "indirect" else None)
    for fig in db.execute("select fig_num,name,num_parts,img_url from minifigs"):
        if any(re.search(p, fig[1]) for p in cfg.get("figure_name_regex", [])) and not any(re.search(p, fig[1]) for p in cfg.get("figure_name_exclude", [])): add(fig, "figure name matches", "name_only")
    for fn, f in found.items():
        f["sets"] = [dict(set_num=sn, name=n, year=y) for sn, n, y in db.execute("select distinct s.set_num,s.name,s.year from inventory_minifigs im join inventories i on i.id=im.inventory_id join sets s on s.set_num=i.set_num where im.fig_num=? order by s.year", (fn,))]
        f["rebrickable_page"] = "https://rebrickable.com/minifigs/%s/" % fn; f["rebrickable_page_note"] = "standard URL pattern of the catalogue ; page itself not fetched (site returns 403 to this environment)"
        f["dimensions"] = "taille minifigurine standard : emprise 2x2 tenons, hauteur ~4 cm (valeur generique de la gamme, NON mesuree sur cette reference)"
        f["availability"] = "non verifie"; f["price"] = None; f["lego_official_id"] = None; f["bricklink_id"] = None
        f["model_3d"] = "aucun modele LDraw exact dans ce depot : integration 3D NON validee (aucun modele fabrique)"
        f["image_file"] = None
        if images and f["image_url"]:
            p = os.path.join(HERE, "cache", "images", fn + ".jpg")
            if not os.path.exists(p):
                try: open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(f["image_url"], headers={"User-Agent": "lego-maps-research"}), timeout=20).read())
                except Exception as e: f["image_error"] = str(e)[:60]
            if os.path.exists(p) and os.path.getsize(p) > 500: f["image_file"] = "cache/images/%s.jpg" % fn
    order = {"strong": 0, "indirect": 1, "name_only": 2}; res = sorted(found.values(), key=lambda f: (order.get(f["relevance"], 3), f["name"]))
    sources = dict(rebrickable_catalogue="local snapshot rb.db, lov=%s" % snap, bricklink=dict(url="https://www.bricklink.com/catalogList.asp?catType=M", http=probe("https://www.bricklink.com/catalogList.asp?catType=M"), used=False),
                   lego_official=dict(url="https://www.lego.com/", http=probe("https://www.lego.com/en-us/search?q=minifigure"), used=False), rebrickable_site=dict(http=probe("https://rebrickable.com/minifigs/"), used=False))
    out = dict(theme=theme, label=cfg["label"], n=len(res), verdict=("Aucune figurine verifiee" if not res else "%d figurine(s) catalogue(es)" % len(res)), sources=sources, candidates=res)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", theme + "_candidates.json"), "w"), indent=1, ensure_ascii=False); return out
if __name__ == "__main__":
    o = search(sys.argv[1], "--no-images" not in sys.argv); print(o["theme"], o["verdict"], {k: (v.get("http") if isinstance(v, dict) else v) for k, v in o["sources"].items()})
    for f in o["candidates"]: print(" ", f["relevance"], f["fig_num"], f["name"][:60], "|", ", ".join(s["set_num"] for s in f["sets"]), "| img", bool(f["image_file"]))
