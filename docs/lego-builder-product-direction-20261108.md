# LEGO Builder — direction produit et état initial (2026-11-08)

## Décision
Fiabiliser les moteurs **avant** toute commercialisation. Aucun achat de machine/pièces, aucune fusion dans main et aucune annonce de produit vendable sans validation.

## Offres cibles
1. Fichiers numériques : notice PDF, BOM vérifiée, modèle 3D, instructions d'approvisionnement.
2. Kit en briques authentiques : pièces approvisionnées, contrôlées, emballées et notice.
3. Kit de briques imprimées en 3D : pièces compatibles, notice et test physique des tolérances.
4. Tableau/sculpture en modules imprimés : relief style briques, assemblage simplifié.
5. Modèle monté : uniquement sur devis, option non prioritaire.

## État de référence — à confirmer par exécution
| Sous-système | Dernier résultat rapporté | Statut |
|---|---|---|
| Maps | V0.8 Premium Italie 19/25, seuil 20/25 non atteint ; quatre cartes techniquement valides | GO technique limité / NO-GO artistique |
| Sculptures | Beagle fidèle ; Paco V8.2 ~2756 pièces, 326 étapes, fidélité des couleurs et bouche perfectibles | GO limité |
| Photo vers modèle/GLB arbitraire | Résultat visuel encore insuffisant | NO-GO |
| Builder unifié | 8 modèles identiques lors de la campagne de non-régression rapportée | À rejouer |
| Export Bambu | Pas d'essai physique ni pipeline validé | NON VALIDÉ |

Ces résultats proviennent des comptes rendus précédents, **pas** d'une nouvelle campagne de tests. Les preuves, SHA, artefacts et scripts doivent être rattachés avant changement de statut.

## Architecture cible
Entrée (carte/photo/GLB) -> moteur géométrie/couleur -> représentation canonique des pièces/modules -> validateurs indépendants -> sorties :
- `lego-bom` : BOM pièce×couleur, coût réel sourcé, notice et achats ;
- `print-bricks` : pièces individuelles STL/3MF, orientation, tolérances, plateaux, temps/masse ;
- `print-modules` : panneaux/volumes segmentés pour plateau 256×256 mm, connecteurs et assemblage ;
- `digital-kit` : package contrôlé, notice, licences et métadonnées.

Les exports doivent rester **facultatifs** et ne pas modifier les résultats des moteurs validés. Ne pas présumer que Brickalike est open source ni que ses géométries sont librement réutilisables commercialement. Auditer les licences LDraw, Rebrickable, les marques et les modèles sous droits.

## Campagne de qualification — avant développement d'un catalogue
1. Figer SHA, dépendances, baselines et cas de tests sur chaque branche ; rejouer la non-régression.
2. Maps : Écosse, Italie, Hyrule et cas indépendants ; collisions, connexions, porteuses, silhouette, lisibilité, rendu face/oblique et score artistique.
3. Sculptures : Paco et Beagle ; forme, couleurs, détails, stabilité, nomenclature, notice, disponibilité.
4. Photos -> 3D : comparer aux vues de référence et interdire tout GO sans validation visuelle.
5. Prototype d'export sur **Hyrule + Paco** : BOM -> géométries de pièces, puis modules monoblocs ; générer fichiers ouvrables dans Bambu Studio, mesurer matière, durée, nombre de plateaux, changements de couleur et coûts.
6. Imprimer un échantillon de tolérances, tester ajustement, tenue et vieillissement ; pas de revendication de compatibilité physique avant mesure.
7. Comparer trois scénarios : achat de briques, impression individuelle, impression modulaire. Comptabiliser échecs, énergie, main-d'œuvre, consommables, amortissement, conditionnement et expédition.

## Portes de décision
- Technique : zéro collision et déconnexion, BOM/notice cohérentes, fichiers ouverts sans erreur ; écarts structurels documentés.
- Artistique : Maps >=20/25 sur la grille choisie ; sculptures validées visuellement par vues multiples.
- Physique : emboîtements et résistance contrôlés sur prototypes.
- Commercial : marge contributive cible >40 % après coûts directs documentés, sans hypothèse de prix inventée.
- Si deux itérations ne passent pas les critères : NO-GO de la sortie concernée, sans dégrader le moteur principal.

## Prochaine action
Inventorier les commits et rapports des branches Maps/Brickify/Unified, produire une matrice de preuves, puis coder un exporteur expérimental isolé. Ne pas démarrer de production commerciale.
