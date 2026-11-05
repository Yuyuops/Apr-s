# Rapport final — LEGO Maps V0.8 (Premium constructible)
Branche `research/lego-maps-premium-feasible-v08` (base : `research/lego-maps-v07-engine2-final`, commit de préparation `bda7aec` ; le commit de livraison est le dernier de la branche). Workflow CI `lego-maps-premium-feasible.yml` : run n°1 réussi (artefact récupéré, 2 styles initiaux validés 0/0/0/0). Génération locale reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (7 à 8 s par carte), puis `check_render.py --no-render`, `verify_bom.py`, `render_views.py`, `fragility.py`, `notice_steps.py`, `make_step_pdf.py`. Données : Natural Earth admin-0 10 m (domaine public, commit épinglé).

## Décision
- **Moteur 2 : NO-GO artistique strict** — Italie 19/25 < 20 après les 2 cycles autorisés. Aucune carte ne dépasse 19 ; aucun critère < 3.
- **Technique : GO sur 4 cartes** pour le niveau « existence catalogue » (0 collision, 0 déconnexion, 0 îlot, 0 non supporté, 0 substitution, 0 îlot géographique perdu, concordance modèle/nomenclature/notice).
- **Disponibilité commerciale et résistance physique : non validées.** Aucun budget (pas de prix vérifié). Aucun achat.
- **Moteur 1 : amélioration vérifiée de la vitesse (×4–4,6, sorties identiques) ; constructibilité inchangée.**

## Réponses aux 5 questions
1. **Style retenu :** Premium Noyer/Or/Lagon (cadre Dark Brown, filets et médaillons or, mer Pale Blue + Light Aqua, strates de 3 plaques, titre blanc en haut). Note **19/25** (V0.7 : 17 sur la même grille ; fidélité historique 15/25, inchangée). Le style Ivoire plafonne à 17.
2. **Cartes générées et validées techniquement :** Italie, Écosse, Japon, Royaume-Uni (compositions génériques, aucune règle propre à l'Italie ; seul ajout : police de titre complétée, option îlots).
3. **Pièces :** Italie 13 633 (111 réf.), Écosse 13 676 (103), Japon 11 477 (110), Royaume-Uni 13 228 (105). **Budget : non estimé** (aucun prix vérifié).
4. **Moteur 1 :** accélération de `fragility.py` (107 s → 23 s sur l'Italie), prouvée identique. Pas d'autre gain démontré.
5. **Prêts pour des modèles personnalisés ?** Le pipeline produit des modèles LDraw valides, avec nomenclature et notice cohérentes, sur plusieurs géographies. Il n'est **pas** prêt à être déclaré « Premium validé » : 19/25, relief de face faible, pas de stock ni d'essai physique.

## Fonctionnalités validées
Cadre premium (filets/médaillons en pièces réelles) ; titre propre (tenons limités aux lettres) ; compositions génériques ; conservation des îlots ; polices étendues (C, J, P, U, K, B, D, G, H, V, W, Y, F, Z) ; notice et nomenclature cohérentes.
## Abandonné
Compas décoratif (flou), palette D, pentes courbes généralisées, ornements en points, XML BrickLink (pas de correspondance couleurs vérifiée).
## Défauts résiduels
Escalier côtier ; relief peu lisible de face ; Angleterre en brun sur la carte d'Écosse ; Ryukyu/Shetland hors cadre ; îlots exagérés à 1 tenon ; notice sans images 3D ; CI non relancée.
## Pour franchir 20/25 (une seule piste, non lancée)
Gagner un point de relief en vue de face (contraste tonal entre strates avec des couleurs catalogues vérifiées) — sans l'inventer ni dégrader la composition.
