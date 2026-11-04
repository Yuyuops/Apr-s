# LEGO Maps Italie V0.5.5 — porte qualité : relief sculpté, Colisée, modules, Italie complète

Branche `research/lego-maps-italie-v055-quality-gate` (départ : `...v054-sector-pilot`). Aucun achat, moteur 1 inchangé, pas de fusion dans `main`, **aucun essai physique**. Tous les rendus viennent de modèles LDraw (géométrie réelle des pièces) ; aucune image générative. Les mesures mécaniques sont indicatives (modèle rigide du validateur).

## Cycle et leçons
| Cycle | Observé | Corrigé | Effet |
|---|---|---|---|
| A1 | Alpes réelles : crête continue, plaine plate | VE 1,45 → 2,1, vallées/crêtes TPI | relief mieux marqué ; hauteur plafonnée par la règle « une brique par tenon » |
| A2 | murs de colonnes verticales (« accumulation de colonnes ») | **pentes 65° (60481, 3678b) et 75° (4460a, 3684a)** sur les ruptures de 2 et 3 briques, en plus des 45° | colonnes remplacées par des tours à flancs inclinés ; neige sur les sommets |
| A3 | tout gris, neige absente | lignes de neige/roche déclarées (1900/1200 m), couleur prise au sommet de la pente | sommets blancs, strates grises |
| B1 | tous les Colisées ≤ 18×22 = boîtes à arcades | test d'échelle : ovale lisible dès 20×26 avec exposant 2,6–2,8 | variante « icône » 20×26 retenue |
| B2 | tout Colisée lisible masque le littoral (34–77 % de la largeur locale) | politique **médaillon offshore** (≥ 96 % de mer) | péninsule intacte ; Colisée à 186 km de Rome (déclaré) |
| E1→E3 | bande d'arrière-pays de 6 tenons grossit le nord ; Colisée trop grand | bande 3 tenons, Colisée 20×26 | silhouette de la botte reconnaissable |

## Chantier A — massif alpin (`results/A_alpes`, `comparatifs/A_V053_vs_V055_*.png`)
Altitude réelle (Terrain Tiles) → champ par tenon → crêtes (position topographique positive), vallées (négative), bruit en crête proportionnel au relief local, exagération verticale déclarée **VE 2,0**, lignes de neige/forêt déclarées abaissées → briques → pentes 45°/65°/75° (142/122/66 pièces) → neige/roche/forêt par altitude et exposition → 25 conifères solides. 32×32 tenons, 1 212 pièces, 0/0/0/0, 114/114 références catalogue. **Au moins aussi expressif que la montagne artistique V0.5.3** (même échelle, 4 vues) et respecte les grandes structures réelles (arc alpin, plaine du Pô, lac/côte). Limite : aspect « dents » accentué par les pentes 75° ; 245 pièces à un tenon (38 décoratives).

## Chantier B — Colisée (`results/B_colisee`, `comparatifs/B_colisee_*`)
Mesures sur la géographie réelle (22×28) : priorité-terre 432 cellules de terre masquées / 227 niveaux de relief ; sea-podium 320 / 197 ; **médaillon offshore 20 / 0, à 186 km de la position vraie** (20×26 : 20 cellules masquées). Variantes plein 18×22, simplifié 15×18, icône 14×17 : **toutes trois sont des boîtes** à ce gabarit (ovale perdu par la quantification) → rejetées (`B_colisee_variantes_*`). `B_colisee_echelle_ovale.png` montre que l'ovale tient à partir de 20×26. Réserve : à 20×26 les arcades sont peu nombreuses (arches 3659/4490 sur les seuls tronçons rectilignes) ; reconnaissance = ovale + gradins + ruine, pas la façade.

## Chantier D — modules (`results/D_modules`, `comparatifs/D_modules_pise_vesuve.png`)
**Tour de Pise** (`pisa.py`) : 8 étages en briques rondes 2×2, étages 1–6 en briques « grille » (loggias), décalage d'un tenon par palier (inclinaison visible, 2 tenons minimum par liaison), 13 pièces + socle ; 600 pièces avec terrain de test, 0/0/0/0. Reconnaissable ; l'inclinaison est en paliers (pas lisse) et la tour est haute par rapport au terrain. **Vésuve** : cône fusionné au relief réel, cratère, arc de la Somma, couleurs de lave ; 691 pièces, 0/0/0/0. **Partiel** : cône et couronne sombre lisibles mais le cratère se lit comme un bloc noir, pas encore un cratère net. Chacun : LDraw, nomenclature (`parts_list.csv`, `bom_verification.csv`), tests, rendus.

## Chantier E — Italie complète 128 × 128 (`results/E_italie/it_v3`)
Champ 102,4 cm (105,6 cm avec cadre de 2 tenons), **9 718 pièces, 211 références, 10,5 kg estimés (±30 %)**, hauteur max 125 mm. Relief réel sculpté partout (Alpes, Apennins, Calabre, Sicile, Sardaigne), Vésuve et Pise intégrés au relief, Colisée en médaillon, 27 terrasses de conifères solides, plages, **mer lissée en tuiles (≈ 2 700 tuiles) dégradée en 3 bleus**, titre **ITALIA** (police 5×7, tuiles) et **rose des vents** (tuiles), cadre brun + chape de tuiles. Plan de montage : `assembly_plan.json` (335 étapes ≤ 40 pièces, par secteur 32×32 et par couche ; sous-ensembles monuments non coupés), `bom_by_sector.csv` ; les LDraw contiennent un `0 STEP` par couche. Pas de notice PDF imprimée. Vues : `renders/full_*`, `alpes_*`, `colisee_*`, `pise`, `vesuve`, `titre`, `rose_des_vents`, `cadre_coin`, `littoral_tyrrhenien`.
Validation indépendante (moteur 1) : **0 collision, 0 pièce déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué** ; LDraw = JSON = nomenclature = 9 718 ; 211/211 couples pièce/couleur catalogués Rebrickable, `.dat` réels non-alias. Prix/stock non vérifiés.
Fragilité (indicative) : 1 526 pièces tenues par 1 tenon (781 feuilles décoratives, 745 portant d'autres pièces), 997 points d'articulation, pire perte isolée 23 pièces / 16,4 g. Aucun essai physique ; accrochage mural non évalué.

## Limites
1. Colisée à 186 km de Rome, arcades peu lisibles à 20×26 ; il touche visuellement la Sardaigne ; la chaussée de liaison (tuiles dark tan) est quasi invisible.
2. Vésuve : cratère peu net ; Pise : inclinaison en paliers.
3. Relief : VE 2,0 et lignes de neige abaissées (déclarées) ; Apennins bas et plats ; flancs alpins en « dents » ; arrière-pays limité à 3 tenons, Corse absente (hors polygone italien).
4. Fragilité : 1 526 pièces à un tenon ; murs de Colisée à 1 tenon d'épaisseur ; aucune validation physique.
5. Nombre de pièces (9 718) sous l'hypothèse 10–25 k, estimation précédente 6,9 k sous-estimée.
