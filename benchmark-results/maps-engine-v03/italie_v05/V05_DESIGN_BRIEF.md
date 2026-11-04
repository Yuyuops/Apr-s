# LEGO Maps V0.5 — spécification de fidélité maximale

**Branche :** `research/lego-maps-italie-v05-quality-first`

## Décision de conception
L'objectif est d'obtenir un tableau décoratif LEGO **proche de la qualité de l'image de référence**, plutôt qu'un budget ou un nombre minimal de pièces. L'image de référence n'est **pas un modèle LEGO validé**.

- **Format d'étude cible :** 128 × 128 tenons (1 024 × 1 024 mm, champ), cadre de 2 tenons de chaque côté => **1 056 × 1 056 mm**.
- **Enveloppe exploratoire de pièces :** 10 000 à 25 000 pièces. **Estimation d'ingénierie non vérifiée**, jamais une nomenclature ni un prix. Un rendement supérieur avec moins de pièces reste préférable.
- **Épaisseur/masse/accrochage :** non figés avant évaluation des données de relief, du rendu et des renforts. **Pas de mise au mur sans dimensionnement et essai physique.**
- **Palette cible :** mer bleu profond, littoral beige, verts nuancés, roche brun/gris, cimes enneigées, ornement crème/doré **uniquement avec des références LEGO existantes**.
- **Contours :** vraie géométrie Natural Earth pour l'Italie, la Sicile et la Sardaigne ; aucun déplacement d'île pour embellir artificiellement la géographie.
- **Relief :** données DEM réelles à intégrer dans une phase suivante ; en V0.5, seule une montagne **de démonstration**, déterministe et explicitement artistique, est autorisée. N'en déduire aucune altitude ou fidélité géographique.
- **Monuments :** sous-modèles paramétriques indépendants des pixels. Une architecture reconnaissable, connectée et réalisable, pas une texture ou une illustration superposée.
- **Décor :** lettrage et rose des vents construits comme assemblages de pièces, pas rasterisés à 3 tenons de haut.

## Premier test livrable : deux modules dans un diorama LEGO réel

La preuve V0.5 est volontairement **petite (48 × 32 tenons)** pour minimiser le risque de développer une Italie de 1 m avant d'avoir prouvé les deux capacités manquantes.

- **Module A — Montagne :** géométrie volumétrique à plusieurs sommets et des pentes LEGO `3039`, hauteur maximale environ 57,6 mm hors mer. Aucun rendu IA. Le modèle reste un prototype géométrique, pas encore une représentation des vraies Alpes.
- **Module B — Colisée :** amphithéâtre miniature construit par deux niveaux de piliers cylindriques, des linteaux au-dessus d'ouvertures réellement vides et des gradins en anneau ; échelle d'étude, pas une maquette architecturale fidèle.
- **Socle :** double couche croisée de plaques avec chevauchement des joints, mer et monuments connectés.
- **Sorties exigées :** LDraw, JSON de placements, nomenclature avec prix/stock non vérifiés, vues PNG provenant des maillages des pièces LDraw et validation indépendante du moteur 1.

## Décision GO / NO-GO

**GO vers Italie 128 × 128** uniquement si :
1. Le relief est clairement volumétrique et reconnaissable en vue de trois quarts.
2. Le monument est reconnaissable **sans** le légender.
3. Les pièces et couleurs existent réellement dans LDraw ; les références difficiles sont documentées.
4. Zéro collision, zéro pièce déconnectée, zéro pose sans appui dans les validations numériques.
5. Les performances et la nomenclature restent explicables, et les supports critiques sont mesurés séparément.

**NO-GO / CORRIGER** si la montagne reste un empilement de cubes sans pentes lisibles, si le Colisée ne présente pas de vraies ouvertures, ou si les vérifications LDraw échouent. Ne pas modifier les seuils des tests pour obtenir un verdict favorable.

Après validation seulement : relief DEM, véritables sous-modèles de monuments, végétation, cadre décoratif, rendu complet du tableau 128². On pourra alors tester 96² et 64² pour établir le compromis rendu / coût.

Aucun achat, aucun calcul de stock fictif, aucune fusion `main`, aucun changement au moteur 1. Les tests physiques et la fixation murale restent à réaliser.
