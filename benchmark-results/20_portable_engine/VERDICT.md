# Verdict V11

## VALIDER V11 (avec réserves explicites)

**Les deux modèles ont été régénérés depuis un nouveau clone, sans `~/bench`, sans fichier temporaire ni chemin de l'ancien environnement.**
* **Paco** : modèle brut **identique à l'octet** à V9.1 (204 s).
* **Beagle** : modèle brut **identique à l'octet** à V10 avec la base Rebrickable de référence ; avec la base téléchargée aujourd'hui, **86 pièces en plus et 123 en moins** (1 % du modèle), **expliquées par la dérive de la base** (une plaque 1×3 Dark Brown passe de 19 à 20 sets) et mesurées (`REPRODUCTION.md` § 3).
* Dépendances Python et Node **verrouillées**, `brickify` et LDraw **aux commits exacts**, empreintes de contrôle, GLB lus **directement** (couleurs par sommets), commande standard `lego_run.py`, 9 tests portables réussis, références historiques intactes (38 empreintes).

## Réserves

1. **La base Rebrickable n'est pas figeable** : la reproductibilité exacte du Beagle dépend d'une version que l'amont ne conserve pas. Dérive mesurée et reproductible à l'octet si la base de référence est fournie (`LEGO_DEPS`), mais non récupérable depuis Internet. À traiter : extraire dans Git le sous-ensemble de disponibilités nécessaire, si la licence le permet.
2. **Le module d'oreille et la segmentation restent propres à Paco** (repère de l'oreille et silhouettes archivés comme données de configuration, règles de bipède) : ils sont reproductibles, pas généraux (verdict de V10 inchangé : généralisation partielle).
3. Les **étapes longues** (plans d'oreilles, notice, PDF) n'ont pas été rejouées dans le clone propre ; leurs entrées le sont.
4. L'**audit de fidélité** révèle des défauts de couleur et de placement non corrigés (`AUDIT_FIDELITE_COULEURS_PLACEMENT.md`) : briques noires visibles sur Paco (237 cellules), briques jaunes et rouges absentes du chien sur le Beagle, yeux du Beagle non détectés. L'affirmation de V10 sur un écart de couleur de 100 sur 255 est **corrigée** (ΔE moyen de 17,1 sur les pièces).

## Pourquoi pas « CORRIGER » ni « ARCHITECTURE À REVOIR »

L'exécution complète depuis un clone propre **réussit** : aucun blocage. Aucune partie essentielle de la génération ne dépend d'un fichier temporaire : les données propres à Paco (repère d'oreille, silhouettes) sont désormais **archivées et déclarées** dans la configuration du sujet. Ce qui est spécifique à Paco est un défaut de généralité (V10), pas de portabilité.

Aucune nouvelle optimisation esthétique n'a été lancée ; les couleurs et la géométrie ne sont pas modifiées.
