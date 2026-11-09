# Sprint V15 — Verdict final : **GO artistique limité (reconnaissance) · NO-GO « premium comparable à la référence » · GO technique non acquis à la lettre**

Aucune fusion dans `main` ; aucun achat ; **aucune référence CI ajoutée ni modifiée** (gel interdit avant validation visuelle humaine) ; reconstruction de V14 identique à la référence `5afb9ac8…` ; le moteur de construction n'a pas été modifié.

## Réponses aux six questions
**1. La détection du besoin existe-t-elle et fonctionne-t-elle ?** Partiellement, et beaucoup moins que prévu : ce qui existait réellement se réduisait à un **classifieur de type heuristique** (`analyze.py`) et un routage par table (`INTENT_DETECTION_AUDIT.md`). Il n'y avait **ni interprétation de la demande, ni extraction de contraintes, ni sémantique d'image, ni détection de version** (jamais implémentés : rien à raccorder). Je n'ai pas refondu : j'ai ajouté un composant minimal, hors ligne et sans API payante (`intent.py`, `semantic_map.py`, manifeste d'exigences structuré, table de versions). Il fonctionne sur 6 cas testés (Hyrule avec/sans version, carte, photos Paco, mosaïque non implémentée, demande vague) et 3 tests unitaires (9/9 verts).

**2. Comment interprète-t-il Hyrule ?** Demande + image + exigences structurées → *carte 2,5D → LEGO Maps*, avec blocage tant que la version n'est pas déclarée. La lecture sémantique de l'image (reconnaître BotW, nommer les régions) est **manuelle** (exigences remplies par l'opérateur) : aucune compréhension d'image n'est simulée.

**3. Quelle version de Hyrule ?** **Breath of the Wild (2017)** : la plaque-titre de la référence l'indique et la disposition le confirme (lecture visuelle, pas OCR). Aucune géographie hybride. **Aucune carte originale séparée n'a été fournie** : l'unique source géographique est l'image LEGO de référence (droits inconnus, non versionnée) ; aucune donnée n'a été inventée.

**4. Résultat avant/après.** `renders/compare_all_vs_reference.jpg` (référence | V14 | B | C | C2 | C3), `compare_C3_vs_reference.jpg`, `compare_C3_vs_V14.jpg`, gros plans montagnes et eaux, vue de côté. V14 : carré, titre géant, volcan et mer méconnaissables. C3 : proportions correctes, mer et littoral, désert, Hebra, volcan à cratère, douves du château, lacs.

**5. Améliorations mesurées** (grille gelée, `PIPELINE_COMPARISON.md`) :
| | A (V14) | B | C3 (retenue) |
|---|---|---|---|
| Erreur de proportions | 18,7 % | 0 % | 0 % |
| Précision pixel vs référence | 0,391 | 0,683 | 0,670 |
| mIoU | 0,249 | 0,507 | 0,493 |
| Erreur moyenne des repères | 0,282 | 0,097 | 0,098 |
| Pièces / références | 10 682 / 134 | 12 543 / 163 | 23 420 / 195 |
| Dimensions | 704 × 704 mm | 832 × 688 | 1 088 × 896 |
| Collisions / déconnectées / îlots / non supportées | 0 | 0 | 0 |
| Reconstruction identique | oui | oui | oui |
**Réserve** : la mesure est en partie circulaire (les rasters B/C viennent de la classification de la référence) ; le gain est surtout la correction des proportions et du placement par le **manifeste**, pas un gain de « beauté » mesuré. Le routage seul n'apporte aucun gain. B atteint déjà presque les mêmes mesures que C3 : C/C2/C3 apportent un gain **visuel** (résolution, relief, volcan), pas mesuré.

**6. Limites restantes.**
- **Qualité premium non atteinte vs la référence** : aucune pente/pièce courbe de relief, pas d'arbres ni d'objets, grandes plages vertes encore visibles, relief bas (le cadre domine de côté), transitions nettes. Limites identifiées : **résolution et représentation des données** (raster 96×78/128×104), **placement des pièces** (pas de décor), **heightmap** (hauteur par classe + gain ; aucune donnée d'altitude, relief estimé). Segmentation suffisante pour les grandes régions.
- **Technique** : la règle gelée « pas plus de 25 % de pièces à 1 tenon / points d'articulation » est **violée en nombre absolu** par B, C, C2, C3 (modèles de 17 à 119 % plus gros) ; en taux : 17,8 % → 20,6–22,2 % (1 tenon), 14,3 % → 15,0–15,7 % (articulation) ; pire défaillance isolée : A 24 pièces, B 45, C 5, C2 4, **C3 35**. Un passage de renfort est nécessaire avant fabrication.
- Titre : volontairement absent de la carte ; plaque séparée non réalisée.
- Notes artistiques = modèle, pas humain.

## Décision
- **GO artistique (critère défini : reconnaissable sans titre et régions bien positionnées)** : mesures atteintes par B, C2, C3 (C échoue sur le repère « neige » : 0,525) et lecture visuelle concordante — **conditionnel à votre validation visuelle**.
- **NO-GO pour affirmer que le modèle égale l'exemple LEGO** (richesse, relief, détails).
- **GO technique non acquis** (règle de fragilité) : pas de fabrication ni de gel CI sans renfort et validation humaine.
- **Variante recommandée pour la revue humaine : C3** (même exactitude que B, plus riche, palette plus calme) ; **B** si l'on préfère un modèle plus petit (832 × 688 mm, 12,5 k pièces).

## Généralisation (§8 de la mission)
Le manifeste (`HYRULE_REQUIREMENTS.json`, schéma `lego_builder.requirements/1`) et le routage `intent` sont génériques : changer sujet, version, référence, prototypes, régions suffit pour une autre carte ; le routage Sculpture/Photos/Mosaïque est testé (3 tests + 6 plans) ; Mosaïque reste **non implémentée** (refus explicite). Aucune API IA payante.

## Décisions nécessaires de votre part
1. Valider (ou refuser) visuellement C3 ou B : gel CI seulement après.
2. Fournir, si disponible, la **carte originale** de BotW pour une vérification indépendante des positions.
3. Choisir la taille (832 × 688 mm ou 1 088 × 896 mm) et décider si la plaque-titre séparée doit être développée.
4. Décider d'un éventuel travail moteur (pentes/pièces courbes/décor) si l'objectif est l'égalité avec la référence — hors périmètre de ce sprint.
