# LEGO Maps Italie V0.5.6 — raffinement artistique

Branche `research/lego-maps-italie-v056-artistic-refinement` (départ V0.5.5). Rendus = géométrie LDraw réelle, aucune image générative. Aucun achat, moteur 1 inchangé, pas de fusion dans `main`, **aucun essai physique**. Aucun seuil de validation modifié.

## Chantier 1 — Colisée (3 variantes réellement différentes, 20×26, `comparatifs/B_colisee_3_variantes_facade.png`)
- **A arcades continues** (retenue) : étage bas et étage haut en arches 6182 (4 tenons) et fenêtres 60592 (2 tenons), murs pleins à appareil décalé pour les restes, attique à fentes, corniche, cavea à 7 gradins, ruine asymétrique ; 751 pièces, 129 pièces à un tenon (283 avant le pavage décalé).
- **B colonnade pilier/linteau** : piliers 1×1/1×2 en alternance avec baies, trois niveaux, plaques de linteau ; 817 pièces, 148 pièces à un tenon. Moins lisible (ouvertures étroites).
- **C galeries concentriques** : mur extérieur arcadé + déambulatoire voûté + mur intérieur ; 726 pièces, 74 pièces à un tenon, cavea réduite (moins reconnaissable vu de dessus).
Les trois variantes : 0 collision, 0 déconnexion, 0 îlot, 0 pose sans appui, références catalogue valides. Une version « oval aligné sur pas de 2 » a été essayée et **abandonnée** : l'ovale devenait un octogone.
Limites : les arches n'existent que sur les facettes rectilignes ; sur les pans courbes (escaliers de briques), murs pleins. Reconnaissable à la façade de face, moins en vue rasante.
**Positionnement** : médaillon offshore conservé, déplacé en mer ouverte à l'ouest avec ≥ 3 tenons de mer partout (aucun chevauchement avec la Sardaigne, vérifié par dilatation du masque de terre), lien de tuiles blanches vers Rome (position vraie inchangée, côtes inchangées). Distance déclarée : 308 km. `results/B_colisee/placement_options.*`.

## Chantier 2 — Vésuve (`comparatifs/V055_vs_V056_vesuve*.png`)
Cône unique fusionné au relief (plus d'anneau Somma séparé : épaulement asymétrique au nord), bord de cratère irrégulier (harmoniques), brèche au sud-ouest, cavité de 3 briques de profondeur, parois inclinées (pentes 45/65/75°), teintes cendre/rouille/gris, sol sombre limité au centre. 704 pièces (module), 0/0/0/0. Résultat : une vraie dépression lisible en gros plan ; à l'échelle de l'Italie (cratère ≈ 6 tenons = 5 cm) la cavité reste modeste.

## Chantier 3 — Relief (`comparatifs/V055_vs_V056_alpes_*.png`)
Résultats topographiques V0.5.5 conservés (mêmes altitudes, mêmes vallées). Pentes 75° plus rares (probabilité 0,45, relais par 65°/45°), ouverture 2×2 des spikes d'une seule brique, ligne de roche à 1 000 m (contraste Apennins), pavage groupé. Hauteur max Alpes 12 → 11 briques (−9,6 mm) ; fenêtre alpine 1 219 → 1 031 pièces. Pas de pièces wedge/curved supplémentaires : les pentes 3-largeurs existantes suffisent et l'ajout de nouvelles géométries aurait demandé une vérification de connexion non faite ici.

## Chantier 4 — Fragilité (`fragility.json`, `fragility_V055_reference.json`)
| | V0.5.5 | V0.5.6 |
|---|---|---|
| Pièces | 9 718 | **9 507** |
| À un tenon | 1 526 | **1 181** (−23 %) |
| … portant d'autres pièces | 745 | **426** (−43 %) |
| Montagne à un tenon / portant | 749 / 601 | **396 / 295** |
| Points d'articulation | 997 | 1 076 (+8 %) |
| Pire perte isolée | 16,4 g (mer) | 10,0 g (base Pise, 9 pièces) |
| Murs de Colisée à 1 tenon d'épaisseur | 130 | **25** |
| Masse estimée (±30 %) | 10,5 kg | 10,4 kg |
Causes traitées : (1) cellules de couleur isolées → briques 1×1 sur un tenon : **dégranulation des couleurs** par couche (une cellule sans voisine de même couleur prend la couleur majoritaire) ; (2) piliers 1×1 empilés de façade → pavage de murs 1×N à appui, deux courses décalées ; (3) fusion neutre de pièces adjacentes de même couleur (`scene.merge_pass`) ; (4) ouverture 2×2 du relief. **Non résolu** : les points d'articulation n'ont pas baissé (plus de pièces larges = plus de nœuds de graphe de petit degré), 558 tuiles de mer à un tenon (décoratives), 755 feuilles décoratives. Résistance calculée ≠ validation physique : `PROTOCOLE_ESSAI.md`.

## Chantier 5 — Composition (`results/E_italie/it_v6`, `comparatifs/V055_vs_V056_full_*`)
9 507 pièces, 216 références, **0 collision, 0 déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué**, LDraw = JSON = nomenclature, 216/216 couples catalogués Rebrickable. Plan : `assembly_plan.json` (323 étapes), `bom_by_sector.csv`, **`notice_montage.pdf`** (23 pages : cover, plan, 17 pages secteur/cadre avec nomenclature, monuments, finitions).
Revue : équilibre mer/relief correct (86 % mer), halo de mer en dégradé trop large autour du médaillon (un « lagon » artificiel) ; titre et rose lisibles ; cadre propre ; Tour de Pise : très simplifiée (8 étages, 13 pièces), reconnaissable mais pas une miniature architecturale.
