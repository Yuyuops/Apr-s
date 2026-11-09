# Sprint V15 — Comparaison des pipelines (grille gelée avant essais : `EVALUATION_GRID_FROZEN.json`)

Trois approches (A, B, C) et **deux cycles de correction** (C2 : relief par massif ; C3 : palette volcanique). Même moteur de construction LEGO Maps, **non modifié** ; B et C ne changent que des **données** (composition, style, rasters de classes issus du manifeste).

## 1. Mesures automatiques (identiques pour toutes les variantes)
| Variante | Proportions (l/h) | Erreur de proportions | Précision pixel vs référence | mIoU | Erreur moyenne des repères | GO artistique mesuré (repères ≤ 0,10 **et** précision ≥ 0,55) |
|---|---|---|---|---|---|---|
| A — pipeline actuel (V14, inchangé) | 1.001 | 0.187 | **0.391** | 0.249 | 0.282 | non |
| B — guidé par le besoin (manifeste + sémantique, 96×78) | 1.231 | 0.000 | **0.683** | 0.507 | 0.097 | **oui** |
| C — hybride (B + bandes d'altitude par classe, 128×104) | 1.230 | 0.001 | **0.693** | 0.515 | 0.177 | non |
| C2 — hybride, relief par massif (cycle 1) | 1.231 | 0.001 | **0.682** | 0.498 | 0.099 | **oui** |
| C3 — C2 + palette volcanique plus calme (cycle 2) | 1.232 | 0.000 | **0.670** | 0.493 | 0.098 | **oui** |

Référence de proportions : 1,231 (mesurée). Pixels classés par la palette propre de chaque variante puis comparés à la carte de classes de la référence sur la grille 96×78 (V14 est donc comparée *étirée*, telle qu'affichée).

### Erreur par repère (fraction de la largeur ; plus grand composant de la famille)
| Variante | neige | désert | mer | pierre | forêt | massif brun |
|---|---|---|---|---|---|---|
| A | 0.404 | 0.052 | 0.197 | 0.866 | 0.143 | 0.031 |
| B | 0.026 | 0.022 | 0.032 | 0.016 | 0.484 | 0.003 |
| C | 0.525 | 0.007 | 0.030 | 0.019 | 0.468 | 0.014 |
| C2 | 0.051 | 0.013 | 0.031 | 0.019 | 0.467 | 0.015 |
| C3 | 0.048 | 0.013 | 0.031 | 0.018 | 0.467 | 0.011 |

**Limite de la mesure** : le repère « forêt » (plus grand composant de forêt) est instable : la forêt de la référence est très fragmentée, d'où 0,47–0,48 pour toutes les variantes B/C ; il pèse ≈ 0,08 dans la moyenne. Il n'a pas été retiré après coup (grille gelée).

### IoU par famille
| Variante | eau | herbe | forêt | désert | pierre | neige | brun/rouille |
|---|---|---|---|---|---|---|---|
| A | 0.12 | 0.35 | 0.17 | 0.47 | 0.20 | 0.13 | 0.30 |
| B | 0.53 | 0.58 | 0.50 | 0.50 | 0.32 | 0.47 | 0.65 |
| C | 0.59 | 0.57 | 0.53 | 0.49 | 0.38 | 0.40 | 0.65 |
| C2 | 0.58 | 0.56 | 0.52 | 0.49 | 0.39 | 0.31 | 0.63 |
| C3 | 0.58 | 0.56 | 0.52 | 0.51 | 0.39 | 0.34 | 0.55 |

### Parts des familles (référence : eau 17,0 %, hors-carte 8,6 %, herbe 16,7 %, forêt 17,9 %, désert 14,1 %, pierre 5,7 %, neige 4,1 %, brun 15,8 % sur la grille 96×78 ; V14 : pas de hors-carte)
| Variante | eau | hors-carte | herbe | forêt | désert | pierre | neige | brun/rouille |
|---|---|---|---|---|---|---|---|---|
| A | 3.5 % | 0.0 % | 22.0 % | 15.5 % | 9.9 % | 24.2 % | 6.8 % | 18.1 % |
| B | 17.0 % | 8.6 % | 16.7 % | 17.9 % | 14.1 % | 5.7 % | 4.1 % | 15.8 % |
| C | 16.5 % | 8.5 % | 14.1 % | 19.7 % | 10.8 % | 12.3 % | 3.2 % | 14.9 % |
| C2 | 16.6 % | 8.7 % | 14.1 % | 19.6 % | 10.5 % | 13.5 % | 2.4 % | 14.6 % |
| C3 | 16.6 % | 10.4 % | 14.1 % | 19.6 % | 10.2 % | 13.5 % | 2.7 % | 12.8 % |

## 2. Mesures techniques
| Variante | Pièces | Références | Dimensions (mm) | Génération + validation (s) | Collisions | Déconnectées | Îlots | Non supportées | Pièces à 1 tenon (taux) | Points d'articulation (taux) | Pire défaillance isolée | Reconstruction identique | SHA-256 LDraw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 10682 | 134 | 704 × 704 | 5 + 35 | 0 | 0 | 0 | 0 | 1898 (17.8 %) | 1532 (14.3 %) | 24 pièces (strata_body) | True | `5afb9ac8fe80f008…` |
| B | 12543 | 163 | 832 × 688 | 6 + 43 | 0 | 0 | 0 | 0 | 2580 (20.6 %) | 1952 (15.6 %) | 45 pièces (strata_body) | True | `882e1293f361447a…` |
| C | 21955 | 188 | 1088 × 896 | 9 + 133 | 0 | 0 | 0 | 0 | 4565 (20.8 %) | 3290 (15.0 %) | 5 pièces (strata_body) | True | `b21c09f722e40b31…` |
| C2 | 23286 | 204 | 1088 × 896 | 10 + 160 | 0 | 0 | 0 | 0 | 5169 (22.2 %) | 3662 (15.7 %) | 4 pièces (frame) | True | `5ce0b3252a39b3e0…` |
| C3 | 23420 | 195 | 1088 × 896 | 9 + 149 | 0 | 0 | 0 | 0 | 5169 (22.1 %) | 3687 (15.7 %) | 35 pièces (strata_body) | True | `27f3fdfe050bfbd8…` |

Temps de rendu (3 vues + gros plans, three.js) : de l'ordre de 1 à 3 min par vue (plus long pour C/C2/C3, 22–23 k pièces) ; non retenu comme critère.

## 3. Critères techniques obligatoires de la grille gelée
- **Zéro collision / déconnectée / îlot / non supportée** : respecté par A, B, C, C2, C3.
- **Génération reproductible** : respecté (deux constructions → même SHA-256).
- **Baselines intactes** : les références de `ci/reference_hashes.json` ne sont pas modifiées ; la reconstruction de V14 redonne exactement `5afb9ac8…` ; aucun fichier de moteur ou de style existant n'a été modifié (uniquement des fichiers nouveaux + une sous-commande `intent` ajoutée au Builder).
- **« Aucun défaut structurel critique nouveau » (règle gelée : pas plus de 25 % de pièces à 1 tenon / points d'articulation en nombre absolu)** : **non respectée à la lettre** par B, C, C2 : leurs nombres absolus dépassent V14 de +36 % à +172 % (1 898 → 2 580 → 4 565 → 5 169 pièces à 1 tenon), **mais** ces modèles ont de 17 % à 118 % de pièces en plus. En taux, la dégradation est limitée (pièces à 1 tenon 17,8 % → 20,6–22,2 % ; points d'articulation 14,3 % → 15,0–15,7 %) et la pire défaillance isolée **diminue** pour C, C2 (24 → 5 et 4 pièces) mais **augmente pour B (45 pièces)**. Verdict technique : **GO technique non acquis au sens strict de la grille** ; une revue de fragilité (renforts) serait nécessaire avant fabrication.

## 4. Régressions éventuelles
Aucune sur les baselines (voir §3). Le titre « HYRULE » n'existe plus sur la carte (volontaire) ; le cadre est inchangé ; la version carrée 80×80 est remplacée par 96×78 (B) ou 128×104 (C…), donc des **modèles plus grands** (832×688 mm et 1088×896 mm contre 704×704 mm).

## 5. Réserve de méthode (à lire avant de conclure)
La mesure est **partiellement circulaire** : les rasters de B et C sont dérivés de la classification de la référence elle-même ; la précision pixel de B/C mesure donc la fidélité de la chaîne *semantic_map → moteur → rendu* à cette classification (déformations de rééchantillonnage, regroupements de pièces, mélange de familles), **pas** une vérification géographique indépendante (il n'existe pas de seconde source : aucune carte originale n'a été fournie). Pour A, l'écart est réel : sa géographie vient d'une autre préparation. La différence A → B/C est donc surtout la preuve que **le manifeste (proportions, zone de carte, classes, hors-carte, absence de titre) corrige la distorsion**, et non que la géographie est « exacte ».

## 6. Gain attribuable à la détection du besoin
- Le **routage** seul (type « carte » → LEGO Maps) existait déjà et était correct pour A : **aucun gain** de rendu à lui attribuer.
- Le gain vient du **manifeste** (proportions mesurées 1,231, rectangle de carte, classes sémantiques dont hors-carte/lacs/cratère, pas de titre) : précision pixel 0,39 → 0,68 (B), erreur de proportions 18,7 % → 0 %, erreur de repères 0,28 → 0,10.
- Le gain supplémentaire de C/C2/C3 sur B est **faible en mesures** (précision 0,67–0,69, mIoU 0,49–0,52 : pas mieux que B) ; il est **visuel** (résolution 128×104 qui sépare mieux les massifs, bandes d'altitude, volcan à cœur sombre), au prix de modèles 2× plus gros (23 k pièces, 1 088 × 896 mm).
