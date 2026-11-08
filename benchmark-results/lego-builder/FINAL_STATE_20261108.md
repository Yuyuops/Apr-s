# État final et verdicts (2026-11-08)
Branche `research/lego-builder-commercial-outputs-20261108`. Détails : `REVALIDATION_20261108.md`, `NOVA_EVALUATION.md`, `BAMBU_EXPORT.md`, `PHOTOS_TO_LEGO.md`, `END_TO_END_TESTS.md`.

## Par moteur
| Moteur | État | Verdict |
|---|---|---|
| Maps (cartes) | reproductible (8 SHA-256 identiques, CI bloquante), 0 collision, 0 déconnexion ; esthétique Italie 19/25 (seuil 20 non atteint, **non amélioré dans cette session**) ; solidité indicative (1 898 pièces à un tenon sur Hyrule) | **GO limité** (technique) ; **NO-GO** artistique |
| Sculptures (Paco, Beagle) | identiques aux modèles acceptés V12.1 ; notice rapide 525 s ; bouche et couleurs de Paco perfectibles | **GO limité** (sujets validés) ; **NO-GO** sujet quelconque |
| Photos → GLB | reproduit exactement les GLB historiques (graine fixe) ; dépend d'un service externe gratuit (délai ajouté) ; aucune photo d'un autre sujet | **GO technique** pour rejouer ; **NO-GO** conversion arbitraire |
| Builder unifié | une commande carte, GLB ou 4 photos ; manifeste strict ; CI bloquante | **GO** |
| Export impression | numériquement valide ; Bambu Studio et imprimante non testés | **expérimental, NO-GO commercial** |
| LDraw Nova | pas de gain mesurable, AGPL | **ne pas intégrer** (contrôle croisé facultatif) |

## Par produit
| Offre | Verdict | Raison |
|---|---|---|
| A. Produit numérique (modèle, notice, nomenclature) | **GO limité** | cartes à données publiques et sculptures validées ; **instructions d'approvisionnement et prix absents** ; Hyrule et personnages sous licence : démonstrateurs internes seulement |
| B. Kit en briques authentiques | **NO-GO (BLOCKED)** | aucune source de prix ni de stock ; pas de contrôle d'approvisionnement |
| C. Briques imprimées | **NO-GO** | tolérances non mesurées, 4 à 5 % de pièces non couvertes, centaines d'heures sur Hyrule |
| D. Modules imprimés | **NO-GO** | non ouvert dans Bambu Studio, aucun essai, approximation par blocs |
| E. Modèle monté | **NO-GO** | rentabilité non démontrée |

## Non fait dans cette session (explicite)
Amélioration artistique de Maps (≥ 20/25), amélioration de la bouche et des couleurs de Paco, test d'un sujet jamais vu, ouverture dans Bambu Studio, essais physiques, prix. Brickalike : introuvable (BLOCKED).
