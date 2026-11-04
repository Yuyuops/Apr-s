# Italia V0.5.4 — pilote transversal Toscane–Rome : VALIDÉ NUMÉRIQUEMENT, REFUSÉ ESTHÉTIQUEMENT

## Traçabilité

- Branche : `research/lego-maps-italie-v054-sector-pilot`
- Run réel : https://github.com/Yuyuops/Apr-s/actions/runs/41883147765
- Artefact : https://github.com/Yuyuops/Apr-s/actions/runs/41883147765/artifacts/13349578699
- Code : `pilot_s11_s12.py`, vues : `views_pilot_v054.json`.
- Entrées conservées : `italia128/output/levels_128.npy`, `placements.json`, Natural Earth + Terrain Tiles attribués dans `fixtures/SOURCES.md`.

## Périmètre

Pilote **64 × 64 tenons, 51,2 × 51,2 cm** (rectangle global lignes 32–95, colonnes 32–95), regroupant S11, S12, S21, S22 afin de ne pas tronquer un Colisée chevauchant S11/S12.

Le relief est calculé à partir des niveaux de Terrain Tiles V0.5.3, mais la géométrie n'utilise pour l'instant que des colonnes et quelques arbres 2×2. Pisa et Vesuvio ne sont PAS intégrés : `modules_not_yet_built`.

## Résultats numériques réellement contrôlés

- **1 363 pièces** et **97 couples pièce/couleur**, BOM et LDraw concordants.
- **64,0 mm** de hauteur maximale du modèle, Colisée inclus.
- **9 conifères** 2×2 solides.
- **0 pente sculptée** ajoutée : le placement des slopes n'a trouvé aucune terrasse assez large et homogène dans ce crop.
- **0 collision**, **0 déconnexion**, **0 îlot**, **0 pose sans appui**, **0 tenon bloqué** au contrôle indépendant.
- **97/97 couples catalogués** selon Rebrickable technique, sans substitutions ; cela ne garantit ni le stock ni le prix.
- Analyse de fragilité indicative : **214 pièces tenues par 1 tenon**, dont **71 portant d'autres pièces** ; **316 points d'articulation** ; pire perte isolée **10 pièces, 12,3 g estimés**. Aucun essai physique, aucune fixation murale vérifiée.
- **9 conifères**, relief maximal géographique du crop seulement 5 niveaux, même si les entrées Italie complète peuvent atteindre 11. Densité trop faible pour l'impact montagne demandé.

## Jugement visuel à partir des rendus LDraw réels

**REFUS ESTHÉTIQUE.** L'objectif est un diorama artistique de qualité, pas une simple botte géographique. Le pilote prouve que géographie, terrain issu de données réelles, sous-modèle Colisée, LDraw et validateurs fonctionnent **dans le même assemblage**. Mais :

1. Le Colisée plein d'environ 18 × 22 tenons prend trop de place relativement à la péninsule centrale ; son socle masque la continuité du relief et des côtes.
2. Les Alpes sont hors du crop Toscane–Rome. Les Apennins présents sont bas et la conversion par colonnes les rend encore trop plats. `slopes_real_LDraw = 0` prouve que le module de montagne sculptée V0.5.3 n'est pas encore effectivement raccordé à l'altitude réelle.
3. L'eau uniforme et apparente occupe une proportion importante ; pas encore de finition cadre, neige détaillée, roches ou monuments secondaires. L'esthétique cible n'est pas démontrée.
4. Les 214 connexions à un tenon, dont 71 porteuses, interdisent de prétendre la solidité physique acquise.

## Décision

**NE PAS LANCER LES 16 SECTEURS.**

Passer à une V0.5.5 strictement ciblée :
- Test A : module de montagne sculptée V0.5.3 conditionné par un champ DEM réel, au-dessus d'une région alpine dédiée (S00/S01), avec une progression visible en 3/4 et des slopes réellement placées.
- Test B : Colisée sur Toscane–Rome, variantes de taille plein 18 × 22 vs simplifié 15 × 18, sinon variante icône conservant l'ovale (pas de petite boîte rectangulaire). Évaluer occupation de la terre, masque du MNT et effet sur le littoral.
- Seulement après ces preuves : assemblage des secteurs et modules Pise/Vésuve, sans budget contraignant à ce stade.

Critère : rendre la montagne et le monument beaux séparément **et ensemble**, via vrais modèles LDraw, avec zéro collision et risques structurels chiffrés. Ne jamais substituer une image générative à une preuve de construction.

Aucun achat, aucun merge main, moteur 1 en lecture seule.
