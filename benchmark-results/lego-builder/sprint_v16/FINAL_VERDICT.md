# Sprint V16 — Verdict final

## Réalisé et prouvé
- Moteur modulaire (options OFF par défaut) : tiler « wild », pénalité d'enveloppement, tuiles « seam », lissage de hauteurs (`smooth_heights`), pentes de falaise, détails par règles, passe de renfort (`--reinforce`). Tests `test_engine_v16.py` 2/2, CI mise à jour.
- 3 zones pilotes (A montagnes, B forêts, C eau/côtes) : relief et détails visiblement enrichis ; pire défaillance isolée 10→7, 14→8, 18→7 ; pièces porteuses à 1 tenon 186→50, 225→34, 158→27 ; 0 collision/déconnectée/îlot/non supportée. Part totale de pièces à 1 tenon **non réduite** (feuilles décoratives).
- Hyrule complet 96×78 (11 187 pièces, validé) : pire défaillance **45 → 17**, mais 1 tenon **20,6 % → 24,3 %**.
- 8 baselines identiques, Italie et Paco identiques via le Builder unifié.

## Limites / échecs déclarés
- Dépassement de la limite de 3 cycles sur la zone A (relief) et sur B/C (correctif eau peu profonde) — déclaré.
- Critère §5 « baisse du % de pièces à 1 tenon » **non atteint** ; passe de renfort 1 sans gain.
- Photos→3D **BLOCKED** (`gradio_client` absent). Tests unitaires/GLB/Beagle non rejoués après les derniers correctifs de repli.
- Détail artistique encore loin de la référence (bâtiments, ponts, chemins, végétation fine). Aucune validation humaine obtenue.
- Les mesures sont numériques ≠ résistance physique ; aucune validation Bambu ; aucune fabrication.

## Verdict (§11)
- **GO reconstruction du Hyrule complet : partiel** — zones améliorées visuellement (jugement de l'auteur), tests structurels de validité PASS, baselines inchangées, pas de nouveau défaut critique de collision ; **mais** critère 1-tenon échoué.
- **GO gel d'une nouvelle version : NON** — exige une validation artistique humaine explicite (absente) et le critère de fragilité n'est pas satisfait.
- **Verdict global : NO-GO pour gel ; candidat expérimental livré** (`ldr/hyrule_V16_full_96x78.ldr`, SHA-256 dans `SHA256SUMS.txt`) pour votre revue visuelle. Aucun gel de référence CI, aucune fusion dans `main`.
