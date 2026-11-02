"""Compare the downloaded Rebrickable database with the reference of the engine (fingerprints in locks/deps.lock.json). Writes the measured drift ; never hides it.
usage: check_rb_db.py <rb.db> <out.json>"""
import hashlib, json, os, sqlite3, sys
lock = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "locks", "deps.lock.json")))["rebrickable_db"]["reference"]
db = sqlite3.connect(sys.argv[1]); out = {}
def table_hash(q):
    h = hashlib.sha256()
    for r in db.execute(q): h.update(repr(r).encode())
    return h.hexdigest()
out["data_timestamp"] = dict(db.execute("select key,value from rb_db_lov").fetchall()).get("data_timestamp")
out["pcs_mat_rows"] = db.execute("select count(*) from pcs_mat").fetchone()[0]
out["sha256_pcs_mat_table"] = table_hash("select part_num,color_id,num_sets,min_year,max_year from pcs_mat order by part_num,color_id")
out["sha256_colors_table"] = table_hash("select id,name,rgb from colors order by id")
out["identique_a_la_reference"] = (out["sha256_pcs_mat_table"] == lock["sha256_pcs_mat_table"] and out["sha256_colors_table"] == lock["sha256_colors_table"])
if not out["identique_a_la_reference"]:
    ref = sqlite3.connect(":memory:")  # row-level drift is measured by tests/test_rb_drift.py when the reference rows are available
    out["avertissement"] = "base Rebrickable differente de la reference (timestamp %s contre %s) : les disponibilites de pieces par couleur peuvent differer ; les ecarts de resultat sont mesures par tests/compare_references.py" % (out["data_timestamp"], lock["data_timestamp"])
json.dump(out, open(sys.argv[2], "w"), indent=1); print(json.dumps(out, indent=1))
