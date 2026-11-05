# Audit de la notice V0.8 et notice illustrée pilote
Branche `research/lego-maps-v09-prototype-hyrule` (base : V0.8 `research/lego-maps-premium-feasible-v08` + correction moteur 1 `research/lego-maps-engine1-fragility-v08`). Style gelé : Premium Noyer/Or/Lagon (`premium_noyer_or_lagon_c2i`), note de référence **19/25 inchangée**. Régénération complète : `style_fidelity_v062/regen_deliverables.sh OUT --render --pdf`.

## Audit de la notice V0.8 (`notice_pas_a_pas.pdf`, générée par `make_step_pdf.py`)
Constat sur pages réelles (page 5 de la carte Royaume-Uni relue en image) :
- **Texte seul** : un bandeau par étape et des lignes « 6x 3460 Dark Bluish Gray rot 90 [Plate 1 x 8] (61,26,0)(0) … ». Aucune image de l'étape ni du sous-ensemble : la compréhension spatiale est laissée au lecteur.
- **Titre faux sur toutes les cartes** : « ITALIA 128 - notice pas a pas » codé en dur, y compris sur Japon, Écosse et Royaume-Uni. **Corrigé** (titre tiré du modèle).
- **Coordonnées trompeuses** : `notice_steps.py` suppose un cadre de 2 tenons (`F = 2`) et un « champ de 128 tenons » ; le style Premium a un cadre de 4. Les positions sont décalées de 2 tenons et peuvent être négatives (`(62,-2,0)`). Notation `(r,c,y)(n)` non expliquée.
- **Remarques de secteurs** (« à cheval sur deux secteurs… ») issues de modules de 32 tenons de l'Italie 128 ; trompeuses sur d'autres tailles.
- **Taille** : 492 étapes pour l'Italie ; 36 pièces maximum par étape ; 17–20 Mo par PDF (pages en images).
- **Points corrects** : ordre bas en haut, regroupement par pièce/couleur/rotation, concordance exacte plan ↔ modèle (vérifiée), avertissements de pièces à un tenon.
Conclusion : cohérente mais **peu exploitable à la main** (pas d'image, repère faux, titre faux).

## Notice illustrée pilote (`make_visual_notice.py`)
Une page par étape : **rendu 3D réel** du sous-ensemble à cette étape, vue recadrée sur la zone modifiée ; pièces à poser en **couleurs vraies**, pièces précédentes en gris clair (convention de dessin, non une substitution de couleur) ; tableau des pièces ajoutées (pastille de couleur, référence, nom, couleur, quantité, rotation, positions « rangée, colonne » à partir du coin nord-ouest du modèle, base 1) ; vérifications de l'étape ; avertissement rouge si des pièces n'ont qu'un tenon. Les remarques de secteurs sont filtrées.
Générée pour les deux prototypes : B 96 étapes et A 133 étapes. Échantillons de pages : `notice_samples/`. PDF complets : artefacts CI et `regen_deliverables.sh --pdf` (non versionnés).

### Est-elle « nettement plus exploitable » ? Réponse nuancée
- **Oui pour le repérage** : l'image montre où poser, les couleurs sont visibles, le repère est correct. C'est un gain réel par rapport au tableau seul.
- **Pas prouvé** pour un montage réel : personne n'a construit à partir de cette notice, **aucun essai**. Je ne déclare pas « notice prête ».
- Limites : (1) étapes de couches de socle entièrement grises/sombres, la mise en évidence y est faible ; (2) pas de pièce isolée en vignette ni de numéros d'appel sur l'image ; (3) 96–133 étapes pour 2,7–3,5 k pièces, regroupement logique encore perfectible (par zone et non par rangées de 36) ; (4) visualiseur 3D interactif `step_viewer.html` généré mais non évalué ; (5) positions en tenons : pas de repères imprimés sur l'image.
### Chantier léger (jours)
Numéroter les pièces sur l'image, vignettes de pièces, regroupement par zone, repères de rangées/colonnes en marge.
### Chantier lourd
Notice type éditeur (sous-ensembles, vues explosées, ordre optimisé pour la main), test utilisateur chronométré.
