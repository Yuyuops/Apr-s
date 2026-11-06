# Verdict final : LEGO Builder (architecture unifiée et import d'images)
Branche `research/lego-builder-unified`. Rien n'a été fusionné dans `main`.

## Ce qui fonctionne (prouvé par les tests)
- **Une commande, de l'image au modèle LEGO vérifié, pour une carte** : `python -m lego_builder run ma_carte.jpg --out … --size-mm 400`. Hyrule : 32 s, 3 245 pièces, 120 références, validé. Aucun masque, aucun JSON, aucune règle écrite à la main.
- **Une commande pour une sculpture à partir d'un GLB** : Paco reproduit **à l'identique** le modèle accepté (V12.1).
- **Non-régression** : Italie et Paco identiques octet à octet ; le code des cartes n'a reçu que deux ajouts génériques (filets de cadre impairs, titre sur terre) sans changer un modèle existant (Italie vérifiée localement ; CI : voir ci-dessous).
- **Cœur commun réel** : validateur structurel du moteur 1, vérification de catalogue, rendus sur les pièces LDraw, nomenclature ; **stratégies de validation distinctes** par famille ; **manifeste** strictement validé (SHA-256 des sources).

## Ce qui ne fonctionne pas encore (limites explicites)
1. **« Des photos de mon chien » → modèle LEGO : non réalisé.** Il manque la reconstruction (un script existe, un service est joignable, **non exécuté dans cette mission**) et la segmentation des sculptures est validée seulement pour Paco (bipède) et le Beagle (quadrupède). Un GLB inconnu reçoit une configuration générique **non validée** ; aucun GLB inconnu n'a été testé.
2. **Fidélité des cartes à partir d'une image** : bonne pour les grandes régions (Hyrule : parts de classes proches du réglage manuel), **approximative pour le recalage et les proportions** (plateau supposé carré, coins ± 5 % de la largeur) et **faible à moyenne** sur la deuxième image (D). Les règles de couleur ont été écrites sur une seule image.
3. **Relief estimé, non mesuré** : aucune altitude réelle n'est lue (pas de carte de hauteur).
4. **Notice** : cartes = plan par couches (PDF et notice illustrée pilote de la V0.9) ; sculptures = plan hiérarchique existant, **non construit dans le test** (plus de 20 minutes). Pas de notice commune.
5. **Mosaïque 2D : non implémentée** (décision documentée).
6. **Solidité** : indicateurs numériques uniquement. Hyrule (auto, 704 mm) : 2 031 pièces à un tenon (1 201 porteuses), 1 582 points d'articulation ; pire défaillance **11,2 g sur le cadre** (V1.0 : 4,4 g) ; **aucun correctif** n'a été fait dans cette mission (pas d'avant/après démontrable).
7. **Disponibilité et coût** : **aucun prix ni stock vérifiable** ; aucun budget donné. **Aucune validation physique.**
8. **Pas d'interface web** : ligne de commande seulement.
9. **Droits des images** : les sources de tiers ne sont pas redistribuées ; le builder n'établit pas les droits.

## Critères de GO
| # | Critère | État |
|---|---|---|
| 1 | Modèles existants reproductibles | **Oui** (Italie, Paco identiques ; autres modèles via la CI) |
| 2 | Les deux générateurs utilisent des services communs | **Oui, partiellement** : validateur, catalogue, rendus, nomenclature ; pas la fragilité ni la notice |
| 3 | Image de carte sans masque manuel | **Oui** |
| 4 | GLB de sculpture sans modification du code | **Oui pour les GLB connus** ; inconnu non testé |
| 5 | Quatre tests avec résultats traçables | **Oui** (`END_TO_END_TESTS.md`, `e2e_results/`) |
| 6 | Livrables cohérents | **Partiellement** (voir limites 4 et 7) |
| 7 | Limites explicites | **Oui** |

## Décision
**GO sous réserves pour la famille « cartes »** : on peut fournir une image de carte et obtenir un modèle LEGO de 40 cm validé au niveau catalogue, avec rendu, nomenclature et plan de montage, sans intervention technique. La fidélité dépend de l'image (voir D).
**GO limité pour les sculptures** : orchestration du moteur 1 démontrée sur un GLB connu (identique à la recette acceptée). **NO-GO** pour annoncer « photos → modèle » ou un GLB quelconque.

## Pour pouvoir dire « voici des photos de mon chien »
1. Brancher et tester la reconstruction multi-vues (service Hugging Face déjà utilisé) dans l'orchestrateur avec contrôle de qualité (vues manquantes, zones peu fiables).
2. Valider la segmentation par la géométrie (posture, appuis) sur un nouveau sujet : c'est la limite principale du moteur 1.
3. Accélérer ou rendre optionnelle la notice hiérarchique.
4. Prix et stock : trouver une source accessible.
