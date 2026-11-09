# Sprint V15 — Analyse de la référence et écarts avec Hyrule V14

## 1. Identification (aucune géographie hybride)
- **Version retenue : Breath of the Wild (2017).** Preuve : la plaque-titre de l'image de référence porte « THE LEGEND OF ZELDA BREATH OF THE WILD » ; la disposition (montagnes enneigées au nord-ouest, désert au sud-ouest, volcan à cratère au nord-est, plaine centrale avec douves du château, mer à l'est) est celle de la carte de BotW. Lecture **visuelle par l'opérateur, pas par OCR automatique** (`HYRULE_REQUIREMENTS.json`).
- **Source géographique unique = l'image de référence** (un modèle LEGO tiers vu de dessus). **Aucune carte originale distincte n'a été fournie** : la demande « utiliser la carte originale pour vérifier les positions » ne peut donc pas être satisfaite autrement que par cette image ; aucune donnée géographique n'a été ajoutée ni inventée. Droits de l'image inconnus : elle n'est **pas versionnée** (SHA-256 `b0d8fdda…0825`), seules les grilles de classes dérivées et les mesures le sont.
- Rectangle de carte mesuré : 1 128 × 916 px → **rapport 1,231 (largeur/hauteur)**. V14 avait supposé une grille carrée 80 × 80 : **distorsion de 18,7 % des proportions** (cause géographique n° 1 de la mauvaise reconnaissance).

## 2. Ce que fait le modèle de référence (techniques LEGO visibles)
| Aspect | Constat sur l'image |
|---|---|
| Construction | plaques et tuiles de petite taille, très nombreuses **plaques rondes 1×1** (arbres, fleurs, repères), plusieurs hauteurs, détails par pièce : tours, ponts, bâtiments, château |
| Relief | massifs enneigés faits de **pentes et pièces courbes blanches/grises** à hauteurs variées ; falaises en pentes brunes ; plaines quasi plates ; cratère creux au centre du volcan |
| Montagnes / falaises / littoraux | contours irréguliers, transitions progressives (blanc → gris → brun → vert) ; littoral à bord sableux clair par endroits |
| Densité de détails | **élevée** : ≈ 650 composantes de classes distinctes à la résolution de mesure (V14 : 253) ; densité de frontières 0,64 contre 0,38 pour V14 |
| Régions | transitions douces ; quatre grandes régions et des dizaines de zones locales (forêts, lacs, rivières) |
| Palette | eau **bleu franc** (baseplate bleue), verts en 2–3 tons (clair, moyen, sombre), sable beige, blanc, gris clair/foncé, bruns tan/orange/rouille ; noir/gris foncé pour le hors-carte |
| Cadre / présentation | cadre **gris foncé** plat, plaque-titre sculptée sous la carte (le cadre bois doré de V14 est notre choix, conservé), titre séparé de la carte |

Part des classes (mesurée sur la référence) : eau 15.0 %, lacs/rivières 3.3 %, hors-carte 4.3 %, herbe 17.1 %, forêt 13.7 %, désert 6.4 %, rivage sombre 4.5 %, pierre 13.1 %, neige 6.3 %, plateau brun 13.0 %, rouille 2.8 %, cratère 0.5 %.

## 3. Écarts critère par critère : référence vs V14 (mesures sur grille 96 × 78, `eval/eval_A.json`)
| Critère | Référence | V14 | Écart / cause |
|---|---|---|---|
| Proportions | 1,231 | 1,001 | grille carrée supposée : géographie étirée verticalement (−18,7 %) |
| Eau | 18,2 % de la carte (+ hors-carte 4,4 %) | **3,5 %** | V14 : le hors-carte et les lacs sont absorbés par la roche/herbe ; la mer est réduite à des bandes — « eau et littoral mal différenciés » |
| Roche grise | 13,1 % | **24,2 %** | V14 : la classe « pierre » déborde sur le hors-carte et les bords (nord-ouest gris uniforme) |
| Brun | 15,6 % (plateau + rouille + cratère) | 18,1 % mais mal placé | V14 : le brun couvre aussi des zones de la référence qui sont blanches/vertes ; reconnaissance du volcan impossible |
| Grandes surfaces vertes | plus grande plage d'herbe 6,3 % | 12,6 % | V14 fusionne herbe et forêt en grandes plages uniformes (forêt sombre sous-représentée) |
| Neige | 6,3 % répartie en 3 massifs | 6,8 % mais fragmentée | position du plus grand massif erronée (repère neige : 0,40 d'erreur) |
| Reconnaissance (accord pixel/classe) | — | **39,1 %**, mIoU 0,249, erreur de repères 0,282 | cf. grille gelée |
| Hors-carte (noir) | 4,4 % | 0 % | V14 n'a pas de classe « hors-carte » : cette zone sombre est rendue en roche grise |
| Titre | plaque séparée, sculptée | **lettres géantes sur la carte** | V14 : titre disproportionné qui masque le volcan ; V15 : aucun titre sur la carte |
| Cadre | gris foncé discret | bois brun + or (voulu) | à conserver ; secondaire à la carte |

## 4. Corrections du pipeline de détection du besoin qui en découlent
1. **Le manifeste doit porter les proportions mesurées** (rapport 1,231) et la zone de carte dans l'image : V14 n'avait ni l'un ni l'autre → déformation. (`board.aspect_width_over_height`, `reference.map_rect_px`.)
2. **Classes sémantiques explicites** (hors-carte, lac, rivage, cratère, variantes d'altitude) définies dans le manifeste et mesurées par prototypes Lab sur la référence elle-même.
3. **Pas de titre sur la carte** (critère de reconnaissance sans titre).
4. **La version de Hyrule doit être déclarée** : l'absence de version bloque (`intent`).
5. Le relief ne vient pas de la couleur seule : zones sémantiques + bandes d'altitude par distance au bord du massif ; hauteurs déclarées *estimées* (aucune donnée d'altitude).

## 5. Ce que le moteur actuel ne permet PAS de reproduire (limites identifiées, pas corrigées dans le moteur)
- **Résolution** : la référence compte des centaines de plaques rondes 1×1 et de petits objets ; un raster de 96 × 78 (ou 128 × 104) ne porte que les grandes zones. Limite : **résolution / représentation des données**.
- **Pièces spéciales** (pentes, pièces courbes blanches, arbres) : le moteur place des plaques/tuiles rectangulaires et arrondies, pas de pentes de relief ni de décor végétal. Limite : **placement des pièces**.
- **Hauteurs** : constantes par classe (+ gain par distance) ; pas de heightmap continue. Limite : **heightmap**.
- **Segmentation** : suffisante pour les grandes régions (cf. aperçu `data/reference_classes_preview.png`) ; les petits repères (tours, bâtiments) ne sont pas segmentés.
