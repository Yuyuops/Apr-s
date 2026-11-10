# Sprint V17 — Analyse multi-vues : objets observés / estimés

Vues exploitables : 1 dessus (750×1000 px), 3 trois-quarts. Recalage : château de la vue de dessus (350, 405) px ↔ cellule (29, 46) de la grille V16 96×78 (il coïncide avec la péninsule « pierre » du raster V16) ; échelle ≈ **5,6 px par plot** (carte ≈ 540 px ↔ 96 plots). **Précision de position estimée : ± 1,5 plot.**

## Zone `centre_chateau_et_plaine` → zone pilote D (32×32 plots, origine (18, 30), `sprint_v17/data/zone_D_classes.*`)
| Objet | Type | Position (ligne, col) | Statut | Taille / hauteur | Assemblage LEGO |
|---|---|---|---|---|---|
| Château central (structure circulaire, 4 pointes) | château | (27–32, 44–49) | **position observée** ; taille **estimée** 6×6 plots (≈ 25 px) ; hauteur **non mesurable** | 18 plaques (choix de la bibliothèque) | `castle` (31 pièces) |
| Tours rondes à anneau brun | tour | (44,43), (24,57) | observées | 2×2 plots ; hauteur choisie | `tower` ×2 |
| Structure ronde sable à centre bleu | tour | (31,31) | observée | 2×2 | `tower` (sable) |
| Bloc noir à point jaune | tour basse | (44,53) | observé | 2×2, 1 brique | `tower` (1 brique) |
| Ponts bruns (≈ 5 dans la zone) | pont | (36,36), (47,34), (36,55), (40,56) | observés (4 reproduits) | 1×3 plots | `bridge` ×4 |
| Rivières (2 bras sud-ouest / sud-est) | rivière | polylignes dans `castle_zone_objects.json` | observées (tracé **estimé**, 1 plot) | largeur 1 | modification du terrain `river` (niveau 2) |
| Chaussée grise au sud du château | chemin | (33–36, 46) | observée | 1 plot | `land` + couleur grise |
| Arbres (vert foncé, très nombreux) | arbre | répartition sur la classe forêt | **densité et variété estimées** | 1×1 ou 2×2 | `tree` ×37 (rond, conifère, petit) |
| Rochers gris | rocher | classe herbe, rares | estimés | 2×2 | `rock` ×4 |
**Non reproduits** (visibles mais hors bibliothèque ou illisibles à cette échelle) : île de fleurs blanches/roses du lac, silhouettes de créatures, petites constructions et enclos, flammes/cônes orange, ≈ 5 ponts hors zone, tours hors zone.

## Ce qui est observé / estimé / inventé
- **Observé** : présence et position approximative des objets ci-dessus.
- **Estimé** : tailles, nombre de plots, tracé des rivières, densité des arbres, couleurs.
- **Non mesurable** : hauteurs, épaisseurs, profils latéraux, détails des façades. Aucune précision géométrique n'est prétendue.
