# LEGO V9.1 : finaliser les oreilles et leur assemblage

Départ : commit `caef2db` (V9, verdict CORRIGER). Le gel du module d'oreille est levé **uniquement** pour la constructibilité. La géométrie V6.1 reste la référence. Aucun achat, aucun déploiement, aucune fusion dans `main`, GLB inchangé, moteur 2 non touché. **Aucun essai physique n'a été réalisé.**

## 1. Ce qui a été trouvé

| Question de V9 | Réponse de V9.1 |
|---|---|
| 31 pièces d'oreille sans séquence | **Erreur du planificateur de V9**, pas du dessin : les 31 pièces sont séquencées, une à une, dans les deux oreilles de Paco, l'oreille V6.1 isolée de Paco et l'oreille du Beagle ; 0 défaut au rejeu avec une géométrie indépendante (`RAPPORT_31_PIECES.md`) |
| Correction du générateur d'oreilles | **Non nécessaire pour l'assemblage** : aucune pièce n'est emprisonnée, la géométrie V6.1 est inchangée (rejeu V6 et V6.1 : AUCUNE DIFFERENCE). Le renfort est un **module après génération** (`stitch.py`), appliqué à Paco et au Beagle |
| 4 groupes de bord d'oreille fragiles | **Renforcés** par des tuiles à cheval sur les joints de plaques : plus aucun cas d'oreille sous 0,5 N, minimum 0,54 N (`RAPPORT_RESISTANCE.md`) |
| Anomalie de masse (310 plaques de plus, 1 118 g inchangé) | **Expliquée** : § 4 |
| 338 pièces par le bas | **Documentées** : le corps (283) reste stable ; les bras (55) doivent être tenus à la main (`RAPPORT_NOTICE.md` § 3) |
| Notice | **Régénérée** : 201 étapes, 5 PDF, vues éclatées, orientation, ordre ; 0 étape en défaut |

## 2. Phases, dans l'ordre du travail

**Phase 1.** Un séquenceur généralisé (`seq.py`) remplace la recherche d'unités rigides : un groupe peut sortir si chaque contact de tenon est libéré par le mouvement et si le volume balayé est libre ; les pièces qui gênent sortent avant (précédence). Mouvements : translations le long des axes des tenons et des axes globaux, puis dégagement de 5 ldu suivi d'un glissement. Contrôle indépendant `verify_seq.py` (autre géométrie, pas de 1 ldu).

**Phase 2.** Non déclenchée : aucune pièce emprisonnée. Le générateur V6.1 est identique (rejeu des entrées archivées : modèles, rapports, validations et nomenclatures identiques). Un script de chaîne générique (`generateur/ear_pipeline.sh`) enchaîne génération, détection des groupes fragiles, renfort, validation et séquençage : il a été appliqué à l'oreille du Beagle.

**Phase 3.** Règle R3 : tuiles à cheval sur les joints de plaques de face (`stitch.py`). Pour Paco : 16 tuiles retirées, 48 ajoutées, 18 tuiles à cheval ; le Beagle : 276 → 294 pièces, 4 groupes de moins de 100 pièces sur 4 résolus. Aucune pièce de structure, aucune nouvelle référence, aucun coefficient modifié.

**Phase 4.** Modèle complet V9.1 (`modeles/paco_V91_brut.ldr`, `paco_V91_notice.ldr`) : voir § 3.

**Phase 5.** Notice (`RAPPORT_NOTICE.md`).

**Phase 6.** Non-régression : § 5.

## 3. Modèle complet V9.1 : vérifications

| Contrôle | V8.2 | V9 | V9.1 |
|---|---:|---:|---:|
| Pièces / types | 2 756 / 42 | 3 066 / 42 | **3 098 / 42** |
| Collisions non autorisées | 0 | 0 | **0** |
| Pièces déconnectées / îlots | 0 / 0 | 0 / 0 | **0 / 0** |
| Tenons bloqués | 0 | 0 | **0** |
| Liaisons de tenons | | 4 849 | 4 899 |
| Pièces sans liaison à la pose (ordre du fichier) | | 18 | **3** |
| Couples pièce × couleur du catalogue | 73 | 73 | **73, tous « vérifiée »** |
| Cas sous 0,5 N / sous 2 N | 50 / 131 | 17 / 77 | **7 / 48** |
| Groupes fragiles | 21 | 8 | **4** (mains, museau) |
| Force minimale | 0,07 N | 0,08 N | **0,19 N** |
| Plan d'appui | 4 plaques, marge 4,2 mm | 26 plaques, 132,2 cm², marge 41,1 mm | **identique à V9** |
| Hauteur du centre de gravité | | 189,5 mm | 189,5 mm |
| Masse du modèle | 1 118,2 g | 1 117,7 g | **1 117,7 g** |

* **Deux chemins de fixation par oreille** : toutes les pièces d'oreille qui ne sont pas des tuiles (donc la plaque principale 2×8, la plaque secondaire cachée et le bloc de racine) sont **identiques** à V9 : mêmes références, positions et matrices (`validation/checks_v91.json`). Les deux chemins sont donc ceux de V7. Le calcul de contacts avec la tête donne 8 pièces de contact (basse) et 7 (haute). L'indépendance mécanique des deux chemins n'a **pas** été recalculée pour V9.1 : elle est héritée du test de V7 (graphe) et des bancs d'essai non encore exécutés.
* **Stabilité sur le plan de contact** : calcul de l'enveloppe convexe des 26 plaques posées au sol et du centre de gravité de la nomenclature : **marge de 41,1 mm**, identique à V9 (aucune pièce hors des oreilles n'a changé). C'est un calcul, **pas une mesure**.
* **Fidélité visuelle** : rendus aux mêmes angles V9 / V9.1 (`comparaisons/`) : 0,051 à 0,117 % des pixels diffèrent (face, profils, trois-quarts, quatre gros plans d'oreille), sans écart de silhouette ni de couleur ; seuls les joints de tuiles de l'oreille basse changent de tracé.
* **Visage et bouche** : les 9 pièces de détail (yeux 43898 et 98138, truffe, pente 54200) sont identiques à V8.2 ; la zone déclarée de la bouche de V8.2 (cases 12 à 27, 78 à 91, 10 à 28) est identique cellule par cellule (occupation et couleur). Test T10.
* **Aucune modification hors zone** : `scope91.py` compare V9 et V9.1 cellule par cellule (occupation, couleur exposée, couleur intérieure, finition) : **0 violation**, 387 cellules de découpage seul (jamais une violation), 16 pièces retirées et 48 ajoutées, toutes des tuiles de face d'oreille, attribuées aux zones d'oreille.

## 4. Masse recalculée à partir de la nomenclature

`nomenclature_complete.csv` (73 lignes, colonnes `masse_modele_g` et `masse_unitaire_modele_g`) ; `validation/mass_cmp.json`.

Le modèle de masse de la validation est : **volume de la boîte de la pièce × fraction pleine × 0,10 g par case de 20 × 20 × 8 ldu**, soit 0,10 g par tenon × tenon × plaque pleine. Il ne dépend que du **volume occupé**, pas du nombre de pièces. Le recoupage de cases déjà occupées (+310 plaques en V9, +32 pièces en V9.1) ne change donc pas la masse : **1 118,18 g (V8.2) → 1 117,68 g (V9) → 1 117,68 g (V9.1)**. La différence de 0,50 g de V9 vient des 5 cases d'appui retirées. L'anomalie de V9 (« 1 118 g inchangé ») n'était **pas** une erreur de calcul, c'était un arrondi (1 118,2 puis 1 117,7).

**Limite** : cette masse est celle du modèle (0,10 g par case), calibrée sur des briques. Les plaques isolées ont une masse par case plus élevée (tenons, parois) ; la masse réelle de la sculpture est donc **probablement supérieure** au chiffre du modèle, mais les masses par référence ne sont pas dans les données disponibles hors ligne : **la masse réelle est inconnue** et doit être pesée (protocole). Les marges de basculement (en millimètres) ne dépendent pas de la masse ; les marges de gravité de la résistance en dépendent.

## 5. Non-régression et tests

| Test | Résultat |
|---|---|
| Rejeu V6 et V6.1 (Paco A, Beagle B ; générateurs `autogen.py` et `autogen61.py` depuis les entrées archivées) | **AUCUNE DIFFERENCE** (modèles, rapports, validations, nomenclatures identiques ; entrées vérifiées par md5) `tests/nonreg_V6_V61_journal.txt` |
| Contrôle de portée T1 à T8 (V9) : erreur de V8.1 rejetée, V8.2 acceptée, changements synthétiques | 10/10 |
| T9 : V9 → V9.1, aucune différence hors des zones d'oreille | **réussi** |
| T10 : V8.2 → V9.1, bouche, yeux, truffe, pente identiques | **réussi** |
| T11 : recoloration d'une plaque de pied hors oreilles | **rejetée** |
| T12 : suppression d'une plaque hors oreilles | **rejetée** |
| T13 : recoloration d'une tuile d'oreille (zone déclarée) | acceptée, attribuée à l'oreille |
| T14 : plaque aile d'oreille déplacée hors de toute zone | **rejetée** (12 violations) |
| Total | **16/16** (`tests/test_scope_v91_resultats.json`) |
| Rejeu du séquençage des oreilles (Paco V9, Paco V9.1, Paco A, Beagle) | 0 défaut |

Amélioration du contrôle de portée dans cette itération : les pièces **hors réseau** (oreilles, plaques tournées) retirées ou ajoutées sont maintenant **attribuées à la zone qui contient leur centre**, et rejetées hors de toute zone (avant, elles étaient seulement comptées). T14 en dépend.

## 6. Archives

Les dossiers 03 à 17 ne sont pas modifiés. Le gabarit de V9 (`17_structural_and_instructions`) reste la référence de comparaison.
