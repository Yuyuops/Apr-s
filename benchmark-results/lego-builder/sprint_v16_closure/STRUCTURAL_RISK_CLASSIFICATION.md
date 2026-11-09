# Clôture V16 — Classification du risque structurel (mêmes définitions sur V15 B et V16)

Outils (committés) : `tools/structural_classify_v16.py`, `tools/weaklink_v16.py`, `tools/pillar_bricks_v16.py`. Entrées : graphe de joints de `validate_v4 --dump` sur `sprint_v15/builds/B/diorama.ldr` et sur `work16/full_rf/pass0/diorama.ldr` (V16, 11 187 pièces). Données : `data/*.json` (une ligne par pièce à 1 tenon, avec position, couche, conséquence).

## Question posée : la solidité de V16 est-elle insuffisante, ou l'indicateur est-il mal adapté ?
**Réponse mesurée : l'indicateur « % de pièces à 1 tenon » (et « points d'articulation ») est mal adapté.** Il mélange trois populations de risques très différents et ignore le nombre de tenons réellement mobilisés. Sur des définitions identiques, V16 est **nettement plus solide que V15 B** sur tout ce qui porte une charge ; la hausse du pourcentage vient uniquement de petits éléments décoratifs.

## 1. Les pièces à 1 tenon en trois catégories
Définitions : **C1 porteuse** = 1 tenon vers le bas ET son retrait coupe ≥ 1 pièce de la plaque de base ; **C2 décorative captée** = rien n'est coupé et aucune colonne voisine n'est plus basse que son sommet (affleurante : ne se retire que verticalement) ; **C3 décorative exposée** = rien n'est coupé et au moins un côté est plus bas (saillie ≥ 1 plaque : peut être heurtée/arrachée latéralement).

| Catégorie | V15 B (12 543 p.) | V16 (11 187 p.) | Évolution |
|---|---|---|---|
| C1 porteuses | **670** (5,3 % des pièces) ; 99 coupent ≥ 4 pièces ; coupe max 7 ; 149 g cumulés | **108** (1,0 %) ; 0 coupe ≥ 4 ; coupe max 3 ; 8 g cumulés | **−84 %**, risque porteur quasi éliminé |
| C2 décoratives captées | 791 (6,3 %) | 733 (6,6 %) | stable |
| C3 décoratives exposées | 1 119 (8,9 %) | **1 879 (16,8 %)** | **+68 %** (c'est la vraie hausse) |
| Total 1 tenon | 2 580 (20,6 %) | 2 720 (24,3 %) | +3,7 pts |

Composition (pièces) : C1 = uniquement des plaques 1×1 (3024). C2 V16 : tuiles 3070b 384, pentes 54200 161, 3024 129, 98138 48. C3 V16 : quarts de rond 25269 **764**, pentes de falaise 54200 **443**, tuiles 3070b 317, 3024 150, **arbres 3062b 134, arbustes/fleurs 6141 71**.

## 2. Localisation (grille 3×3 de la carte, rangées N→S, colonnes O→E)
- C1 V16 (108) : diffuse, 6–20 par secteur, plus nombreuses au centre (20) et au sud-centre (20) ; aucune concentration. V15 B : 39–123 par secteur, maximum au sud-centre (123).
- C3 V16 (1 879) : partout, avec concentration au secteur ouest-centre (327, massifs enneigés/falaises de pentes 54200 et rivages en quarts de rond) ; arbres/fleurs dans les secteurs de forêt/plaine. Par hauteur : 768 aux couches 4–8, 1 111 aux couches ≥ 9 (sommets de relief, donc plus accessibles à la main).
(Détail complet : `data/risk_classes_V15B_V16.json`.)

## 3. Conséquence d'un détachement, renforçabilité, impact esthétique
| | Conséquence | Renforcement possible | Impact esthétique d'une correction |
|---|---|---|---|
| C1 | perte de 1 à 3 pièces voisines (≤ 0,8 g) ; V15 B : jusqu'à 7 | déjà traité par le tiler (−84 %) ; restant : plaques 1×1 de sommets | aucun si fusion en 1×2 de même teinte (possible sur 3 paires seulement) |
| C2 | perte de la seule pièce (tuile/pente affleurante), bloquée latéralement | aucun besoin : retenue latérale par les voisines | — |
| C3 | perte de la seule pièce (≤ 0,6 g), arrachable à la main : **risque d'usage/transport, pas de ruine structurelle** | **limité par la pièce** : 3062b, 6141, 25269, 54200 n'ont qu'un tenon par conception. Fusion « domino » testée : seulement **12 paires** fusionnables sur 1 088 candidates (le tiler les fusionne déjà). Alternative : colle/vernis (hors périmètre), ou remplacer des pièces exposées par des tuiles affleurantes (C2) = perte de détail | **forte** si on retire/aplatit le détail : **non fait** (règle : ne pas supprimer de détails pour améliorer un pourcentage) |

## 4. Indicateur adapté : liens faibles pondérés par les tenons
Un point d'articulation relié à la structure par ≥ 6 tenons (plaque 4×4 de remplissage) n'est pas un lien faible. `weaklink_v16.py` note chaque point d'articulation coupant ≥ 4 pièces par le nombre de tenons le reliant au côté de la plaque de base.

| | V15 B | V16 | V16 corrigé |
|---|---|---|---|
| Pièces | 12 543 | 11 187 | 11 177 |
| Points d'articulation coupant ≥ 4 pièces | 497 | 278 | 268 |
| dont **FAIBLES (≤ 2 tenons)** | **185** | **12** | **3** |
| MOYENS (3–5) / FORTS (≥ 6) | 87 / 225 | 24 / 242 | 24 / 241 |
| Pire défaillance isolée (nb pièces coupées) | 45 | 17 | (17, sur un lien fort 4×4 à 16 tenons) |
| Plus gros groupe coupé par un lien FAIBLE | 10 | 8 | **4** |
| Cas de force de basculement < 0,5 N (validateur) | 76 | 10 | **8** |
| Sous-assemblages > 1 g | 472 | 254 | 252 |
Le « pire cas 17 » de V16 est une plaque 3031 (4×4) retenue par ≥ 6 tenons et portant 2,9 g : c'est un point d'articulation du graphe, pas un lien faible.

## 5. Faiblesses porteuses réelles et correction appliquée
Les 12 liens faibles restants de V16 étaient 3 piliers de plaques 1×2 empilées (aiguilles rocheuses, 9–13 plaques de haut, ≤ 1,6 g). `pillar_bricks_v16.py` remplace 3 plaques 1×2 identiques empilées (même teinte, même empreinte) par 1 brique 1×2 (3004) : **5 remplacements, −10 pièces, 11 177 pièces**. Preuve de non-dégradation du rendu : **occupation voxel + couleur strictement identiques** (94 592 voxels identiques) ; validation indépendante : 0 collision, 0 pièce déconnectée, 0 îlot ; liens faibles 12 → 3 (3 aiguilles de 4 pièces, ≈ 0,8 g, laissées : un pilier 1×2 est faible par construction ; l'élargir changerait la silhouette).
Essai abandonné : division de plaques cachées en deux (`tools/stitch_critical_v16.py`, conservé à titre d'expérience, rapport `data/experiment_split_plates_report.json`) : 36/278 améliorables seulement, car les 242 autres reposent déjà sur ≥ 6 tenons ; gain sans objet.

## 6. Verdict structurel
- **V16 est techniquement acceptable** sur la solidité de la structure : 0 collision/déconnexion/îlot ; liens porteurs faibles 185 → 3 ; cas de basculement < 0,5 N 76 → 8.
- **Risque résiduel réel mais d'une autre nature** : 1 879 petits éléments décoratifs exposés (C3) arrachables à la main (+68 %). À gérer par un **budget d'exposition** en V17, pas par le « % 1 tenon ».
- Les chiffres restent **numériques** ; aucune mesure de force réelle, aucune validation physique.
