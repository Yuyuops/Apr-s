# Prototypes réduits A et B
Branche `research/lego-maps-v09-prototype-hyrule`. Style gelé Premium Noyer/Or/Lagon (`premium_noyer_or_lagon_c2i`), note de référence 19/25. Régénération : `regen_deliverables.sh OUT --render --pdf`.

## Construction des prototypes
Deux fenêtres **autonomes** générées par le moteur (même style, **même échelle en tenons par degré** que les cartes 64×96, cadre noyer de 4 tenons propre). J'ai d'abord essayé de **découper** les sous-ensembles dans le modèle final de l'Italie (`extract_box.py`) : la fermeture des pièces porteuses traîne des « doigts » de socle déchiquetés (boîte englobante 36×88 ou 72×50 tenons, titre coupé en « ITAL ») ; ces prototypes ont été **écartés** (jamais livrés). `extract_box.py` reste dans le dépôt, non utilisé.
| | Prototype A — littoral + relief | Prototype B — cadre + titre |
|---|---|---|
| Composition | `compositions/proto_a_eolie_36x36.json` : îles Éoliennes, nord de la Sicile, pointe de Calabre | `compositions/proto_b_titre_24x48.json` : haut de la carte (Nord de l'Italie, Alpes) |
| Dimensions | 352 × 352 mm (44×44 tenons avec cadre) | 448 × 256 mm (56×32 tenons avec cadre) |
| Pièces / références | **3 489 / 85** | **2 658 / 101** |
| Hauteur max | 76,8 mm | 76,8 mm |
| Contenu | côte, 5 niveaux de strates, terre/mer, **3 îlots conservés** (1 tenon), cadre | cadre noyer, **filets or**, **médaillons or** (4 coins), **titre blanc « ITALIA » complet** |
| Validation (moteur 1) | 0 collision, 0 déconnectée, 0 îlot, 0 non supportée | idem |
| Catalogue | 0 couple non catalogué, 0 substitution | idem |
Rendus : `prototypes/*/renders/{face,trois_quarts,zoom}.png`, vue d'ensemble `prototypes_overview.png`. LDraw, `parts_list.csv`, métriques, fragilité, plan d'assemblage : dans `prototypes/<nom>/`. Notices : `notice_samples/` (échantillons) ; PDF illustrés complets en artefact CI (non versionnés).

## Fragilité indicative (non physique)
| | A | B |
|---|---:|---:|
| Pièces tenues par un seul tenon | 369 | 166 |
| dont décoratives (rien dessus) | 260 | 100 |
| dont porteuses | 109 | 66 |
| Points d'articulation avec perte | 296 | 127 |
| Pire défaillance simple | 5 pièces, 1,8 g (strates) | 5 pièces, **6,4 g (cadre)** |
Concrètement : **48 tuiles rondes or du médaillon** (tenue par un seul tenon chacune, familles `frame_ornament`), **144 / 23 tuiles d'angle arrondi** (A / B), **8 + 3 lettres** du titre, **98 / 47 pièces de strates porteuses à un tenon**.

## Stratégie de montage (issue du plan, à valider à la main)
1. Socle (couches 0 et 1 de plaques) par rangées, croisant les joints avec la couche suivante.
2. Strates par niveau (couches 2 à 23 de plaques), du plus bas au plus haut ; le plan compte 133 étapes (A) et 96 (B), 36 pièces maximum par étape.
3. Surfaces et tuiles de finition, tuiles d'angle arrondi en dernier sur chaque niveau.
4. Titre (B) puis cadre : briques de cadre par couches, tuiles de couverture, filets or, médaillons or **en tout dernier** (pièces les plus fragiles).
Étapes à surveiller : A **66 étapes sur 133** et B **41 sur 96** contiennent au moins une pièce à un seul tenon (l'avertissement rouge de la notice illustrée les signale).

## Étapes ambiguës ou peu robustes
- Étapes de socle (couches 0–1) : pièces grises/sombres, ordre de pose de 36 plaques proche, repérage difficile.
- Médaillons or et lettres : 1 tenon, risque de décrochage à la manipulation ; à pousser avec un outil plat, ne pas serrer le tableau par le cadre.
- Plusieurs couches étroites de strates (1 stud d'emprise) : pas de verrouillage latéral.

## Problèmes concrets et corrections proposées (moteur 1 / moteur 2)
1. **Médaillons or à un tenon** : alternative sans changement d'aspect non identifiée ; remplacer les ronds par des tuiles 1×2 changerait le dessin (dégradation visuelle, refusée). **Non corrigé** ; essai de traction physique requis avant décision.
2. **Cadre : pire défaillance de 6,4 g** (B). Cause probable : tuiles de couverture ou briques de couche supérieure portées par une seule brique du cadre. Correction ciblée proposée : forcer un recouvrement décalé d'au moins un tenon entre cadre et couverture dans le pavage du cadre. **Non implémentée** : aucun essai physique n'a montré le problème ; l'indicateur seul ne justifie pas de modifier le pavage. Aucun avant/après mesuré.
3. Aucune modification de moteur 1 sur cette base (hors accélération de la V0.8).

## Statut
**Exploitables comme prototypes de test de montage et de lisibilité : oui, sous réserve.** Modèles valides au niveau catalogue ; aucune validation physique, aucun stock vérifié, aucun prix. Ils n'ont pas été construits.
