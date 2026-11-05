# Validation de constructibilité (V0.8)
Branche `research/lego-maps-premium-feasible-v08` (base : `research/lego-maps-v07-engine2-final`, commit de préparation `bda7aec` ; le commit de livraison est le dernier de la branche). Workflow CI `lego-maps-premium-feasible.yml` : run n°1 réussi (artefact récupéré, 2 styles initiaux validés 0/0/0/0). Génération locale reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (7 à 8 s par carte), puis `check_render.py --no-render`, `verify_bom.py`, `render_views.py`, `fragility.py`, `notice_steps.py`, `make_step_pdf.py`. Données : Natural Earth admin-0 10 m (domaine public, commit épinglé).

## Trois niveaux, jamais confondus
1. **Existence catalogue — vérifiée** : pour chaque carte, `verify_bom` : tous les .dat existent, couleurs valides, 0 couple pièce/couleur non catalogué ; 0 substitution de couleur ; 0 cellule de repli.
2. **Disponibilité commerciale — NON vérifiée.** Aucun stock ni prix n'a pu être consulté (BrickLink, LEGO.com et rebrickable.com ne sont pas accessibles ici). Présence dans un set Rebrickable ≠ stock. **Aucune estimation budgétaire n'est donnée** (pas de prix vérifié et daté). Aucune commande.
3. **Constructibilité physique — NON validée.** `physical_test: false` ; les indicateurs de fragilité sont numériques, pas des essais.

## Résultats techniques (validateur indépendant du moteur 1, modèle final)
| Carte | Pièces | Réf. | Collisions | Déconnectées | Îlots structurels | Non supportées | Substitutions | Îlots géographiques ≥ 0,25 stud² perdus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Italie | 13 633 | 111 | 0 | 0 | 0 | 0 | 0 | 0 (4 forcés à 1 tenon) |
| Écosse | 13 676 | 103 | 0 | 0 | 0 | 0 | 0 | 0 (18 forcés) |
| Japon | 11 477 | 110 | 0 | 0 | 0 | 0 | 0 | 0 (15 forcés) |
| Royaume-Uni | 13 228 | 105 | 0 | 0 | 0 | 0 | 0 | 0 (10 forcés) |

Îlots : avant correction, 4, 18, 15 et 10 îlots sources (≥ 0,25 stud²) disparaissaient. Option générique `relief.keep_islets` : chaque îlot source est conservé par **un** tenon (exagération cartographique assumée, visible en zoom). Mesure sur le raster Natural Earth à 8 px/tenon. Les îlots plus petits que 0,25 stud² ne sont pas comptés.

## Concordance LDraw / nomenclature / notice (vérifiée par script, 4 cartes)
- Lignes de pièces du `.ldr` = pièces de `parts.json` = quantités de `parts_list.csv` (comparaison par couple pièce/couleur : égalité).
- Les identifiants de pièces du plan de montage (`assembly_plan_v2.json`) sont exactement ceux du modèle : 492, 503, 397 et 470 étapes. 
- La notice PDF (`notice_pas_a_pas.pdf`) est un tableau par étape (pièces groupées, positions) ; compressée en niveaux de gris (qualité 30). Le visualiseur 3D pas à pas (`step_viewer.html`, ~3,7 Mo) est généré mais non livré.
- Nomenclature : `parts_list.csv` et `rebrickable_import.csv` (Part, Color, Quantity, identifiants Rebrickable). **Le XML BrickLink n'est pas généré** : aucune table de correspondance de couleurs BrickLink vérifiée.

## Limites
Aucun essai physique. Relief et escalier côtier limités par la résolution (8 mm/tenon). Écosse : la frontière avec l'Angleterre n'est pas représentée (donnée admin-0). La CI n'a pas été relancée sur les cartes finales.
