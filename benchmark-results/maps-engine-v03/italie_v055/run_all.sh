#!/bin/bash
# V0.5.5 : regenerates every stage (needs the engine-1 environment, see env.sh). Sources are fetched by italia/fetch_sources.py (Natural Earth + Terrain Tiles, see italia/fixtures/SOURCES.md).
cd "$(dirname "$0")"; . ./env.sh
$PY build_catalog.py
# A : Alpine sector from real DEM
$PY alps_test.py results/A_alpes/alps_v1_steep1_VE2.0 --VE 2.0 --detail 8 --ridge_gain 3.2 --valley_depth 6 --sharpen 1.2 --steep 1 --snow_m 1900 --rock_m 1200
# B : Colosseum variants on Tuscany-Rome, scale legibility test, placement policies
$PY colosseum_variants.py results/B_colisee full,simplified,icon; $PY colosseum_variants.py results/B_colisee icon28,icon28_sea
$PY colosseum_scale_test.py work/cs; $PY placement_options.py results/B_colisee 20 26
# D : modules (built through region.py)  /  E : full model
$PY italia_full.py results/E_italie/it_v3; $PY views_italia.py results/E_italie/it_v3
$PY check_render.py results/E_italie/it_v3 --no-render; $PY verify_bom.py results/E_italie/it_v3; $PY fragility.py results/E_italie/it_v3; $PY render_views.py results/E_italie/it_v3 results/E_italie/it_v3/views.json; $PY notice_sectors.py results/E_italie/it_v3
