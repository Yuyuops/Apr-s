# Sprint V15 — Évaluation artistique (grille gelée ; **notes attribuées par le modèle, PAS une validation humaine**)

Rappel : la grille (`EVALUATION_GRID_FROZEN.json`) a été figée avant les essais. Les notes 0–5 ci-dessous sont indicatives (± 1) ; seule la colonne « mesures » est reproductible. Une **validation visuelle humaine est requise** avant de geler une référence en CI (non fait ; aucune référence CI n'a été ajoutée).

## 1. Notes par critère (sur 5)
| Critère | A (V14) | B | C | C2 | **C3** | Justification courte |
|---|---|---|---|---|---|---|
| Reconnaissance géographique (sans titre) | 1 | 4 | 4 | 4 | **4** | A : volcan, mer et neige mal placés, grille carrée ; B/C* : Hebra, Gerudo, volcan à cratère, douves du château, lacs reconnaissables |
| Fidélité à la référence (contours, proportions, eaux) | 1 | 3 | 3 | 3 | **3** | proportions et grandes masses justes ; détails fins (rivières, îlots, repères) perdus |
| Qualité du relief | 2 | 3 | 3 | 3 | **3** | massifs en paliers lisibles, mais relief **bas** (la vue latérale montre un cadre plus haut que le terrain) et marches nettes, pas de pentes |
| Harmonie des couleurs | 2 | 3 | 3 | 3 | **4** | A : gris/brun dominants, eau pâle ; B/C : eau bleu franc, vert 2 tons ; C2 : cœur du volcan rouge vif un peu criard ; C3 : brun foncé plus calme |
| Lisibilité des régions | 2 | 4 | 4 | 4 | **4** | plaines, forêts sombres, désert, roche, neige, eau distincts |
| Cadre et titre | 1 | 4 | 4 | 4 | **4** | A : titre géant sur la carte ; B/C* : pas de titre, cadre conservé (le cadre reste cependant très haut vue de côté) |
| **Total /30** | 9 | 21 | 21 | 21 | **22** | |

## 2. Comparaison critère par critère avec l'exemple LEGO de référence (côte à côte : `renders/compare_*_vs_reference.jpg`)
| Critère | Référence | Meilleure variante (C3) | Écart restant |
|---|---|---|---|
| Géographie / reconnaissance | immédiate | **reconnaissable** (régions et positions justes) | contours plus lisses et plus grossiers |
| Relief et progression | pentes, pièces courbes, hauteurs variées | paliers de 2 plaques jusqu'à 27 plaques (86 mm), teintes d'altitude (blanc/gris, brun clair/foncé) | **pas de pentes ni de pièces courbes de relief** ; relief bas |
| Falaises, littoraux | contours irréguliers, rives sableuses | contours en dents de scie à 8 mm, pas de bord sableux systématique | résolution |
| Densité et variété de détails | très élevée (arbres, fleurs, tours, ponts) | **faible** : régions uniformes (grandes plages vertes encore visibles) | **écart majeur** : limite de résolution et de représentation (le moteur ne place ni arbres ni petits objets) |
| Transitions entre régions | douces | nettes (bordures de classe) | limite du raster de classes |
| Palette | bleu franc, verts variés, sable, blanc, gris, bruns/rouille | proche (bleu, deux verts, sable, blanc, gris, bruns) | verts moins variés |
| Cadre / présentation | cadre gris foncé, plaque-titre sculptée séparée | cadre bois brun/or conservé, **pas de plaque-titre** | titre à créer séparément (hors moteur) |
| Techniques LEGO visibles | plaques rondes 1×1, pentes, tuiles, objets | plaques/tuiles rectangulaires et arrondies, strates | non reproduites |

**Lecture honnête** : notre carte est **reconnaissable et correctement positionnée**, donc elle répond au critère GO artistique défini, mais elle reste **nettement en dessous de l'exemple LEGO en richesse et en finesse** : c'est une carte régionale lisible, pas encore un tableau « premium » comparable à la référence.

## 3. Comparaison avec V14
Voir `renders/compare_B_vs_V14.jpg`, `compare_C3_vs_V14.jpg`, `detail_montagnes_ref_V14_B_C3.jpg`, `detail_littoral_lacs_ref_V14_B_C3.jpg`, `detail_lateral_relief_A_B_C3.jpg`. Améliorations visibles : proportions, mer et littoral, volcan et cratère, massifs enneigés placés, absence de titre géant. Régression : modèle plus grand (C3 : 1 088 × 896 mm, 23 420 pièces) ; relief toujours bas.

## 4. Limites des notes
- Notes du modèle, sans panel humain ; aucune mesure de préférence.
- Le critère « relief » n'a pas d'équivalent automatique (aucune donnée d'altitude dans l'image).
