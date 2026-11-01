# LEGO V6.1 : grands arrondis du générateur automatique

Point de départ : commit `24f999d` (V6). Architecture conservée : seule l'étape de **choix des pièces de forme** change. Extraction, catalogue, intérieur, règles de V5.1, fixation et contrôles sont ceux de V6. Même code et même bibliothèque de pièces pour Paco et pour le Beagle, aucune règle propre à un modèle, aucune position recopiée des prototypes manuels.

## Verdict : **VALIDER V6.1**

**Les grands arrondis sont reproduits automatiquement sur les deux oreilles, et la constructibilité numérique est conservée** : 0 collision avec les deux validateurs, 0 pièce déconnectée, notices réalisables, couples pièce × couleur vérifiés.

**Réserves, hors du périmètre de cette mission :**

- Sur Paco, la **plaque de fixation supérieure reste visible** sur le dessus du crâne. C'est la fixation V6, gardée comme référence et non retouchée.
- Pour le Beagle, **la fixation à une tête n'a pas encore été démontrée** : l'oreille est générée et validée seule.
- Sur Paco, une saillie plate d'une rangée reste à la pointe. Elle suit le court bord vertical du contour extrait du GLB, que V5 avait aussi.

## 1. Ce qui a changé dans l'algorithme (`generateur/autogen61.py`)

| V6 | V6.1 |
|---|---|
| Choix glouton, pièce par pièce | **Programme en nombres entiers** (`scipy.optimize.milp`) limité aux candidats de contour (60 sur Paco, environ 150 sur le Beagle) : les combinaisons de pièces sont évaluées ensemble |
| Arcs non traités en tant que tels | **Arcs continus détectés**, avec leur rayon médian (Paco : 78 LDU ; Beagle : 46, 59, 60, 61 LDU). Un arc de 60 LDU ou plus est **caractéristique** |
| — | **Forte pénalité (400)** si la moitié d'un arc caractéristique n'est pas longée par les bords des pièces choisies. Chaque pixel d'arc n'est compté qu'une fois, ce qui évite qu'une grappe de petites pièces l'emporte artificiellement. Les bords du contour contre le crâne ou une zone interdite ne sont pas des arcs. |
| Une pièce de forme réservait sa boîte rectangulaire | Elle réserve **les cases que touche sa vraie géométrie**. Le vide laissé dans ces cases compte contre elle. |
| `validate_v2` traitait ailes et plaques arrondies comme leur boîte | **`validate_v3`**, nouvelle copie : les pièces qui ne remplissent pas leur boîte sont contrôlées sur leur vraie géométrie. Les résultats sont donnés avec v3 **et** v2 : 0 collision dans les deux cas. |

## 2. Mesures (`mesures_fidelite.json`, un seul protocole pour toutes les versions)

Image au pas de 4 LDU du plan de l'oreille ; contour de la face extérieure, sur la vraie géométrie des pièces.

- **Zone de mesure de Paco :** v ≥ 52 LDU, hors crâne, identique pour V5, V5.1, V6 et V6.1.
- **Extrémités :** les 80 LDU à chaque bout de l'axe principal de la silhouette du GLB. C'est une règle générale : elle désigne le bout libre de Paco comme le haut et le bas tombant du Beagle.

### A : Paco

| | V5 manuelle | V5.1 manuelle | V6 | **V6.1** |
|---|---|---|---|---|
| IoU avec la silhouette du GLB | 0,867 | 0,898 | 0,935 | **0,936** |
| IoU avec la référence manuelle V5 | 1 | 0,903 | 0,864 | 0,867 |
| **Bout libre arrondi** : IoU locale / surface d'écart / écart maximal | 0,910 / 1 024 LDU² / 8,9 LDU | 0,908 / 1 040 / 8,9 | 0,927 / 800 / 8,9 | **0,929 / 784 / 8,9** |
| Arc haut du bout (r 78) : écart moyen / maximal / part à moins de 8 LDU | 4,8 / 8,0 / 100 % | 3,2 / 8,0 / 100 % | 2,7 / 8,0 / 100 % | 3,2 / 8,0 / 100 % |
| Écart maximal contour GLB → contour généré | 63,2 | 40,0 | 20,0 | **20,0** |
| Écart maximal contour généré → contour GLB | 55,6 | 36,9 | 36,9 | 36,9 (au raccord du crâne, commun à toutes les versions sauf V5) |

**Le demi-disque de V5 est-il adapté ?** Pas exactement. Le bout extrait du GLB est **asymétrique** : un arc d'environ 78 LDU de rayon en haut, un bord presque rectiligne en bas. Le demi-disque symétrique de V5 s'écarte de 63 LDU du GLB en bas. Le programme a bien évalué le demi-disque à cette même position : c'était le meilleur candidat isolé. Il retient pourtant un **quart de rond 4×4 en haut et une aile en bas**, qui suivent mieux le contour réel (surface d'écart 784 LDU² contre 1 024 pour V5).

### B : Beagle

| | V6 | **V6.1** |
|---|---|---|
| IoU avec la silhouette du GLB | 0,958 | 0,956 |
| **Bas arrondi** : IoU locale / surface d'écart / écart maximal | 0,909 / 1 552 LDU² / 12,0 LDU | **0,918 / 1 392 / 12,0** |
| **Haut arrondi** : IoU locale / surface d'écart / écart maximal | 0,921 / 1 168 / 11,3 | **0,927 / 1 072 / 11,3** |
| Arcs (r 46 à 61) : écart moyen | 2,6 à 4,9 LDU | 2,7 à 4,9 LDU |
| Écart maximal GLB → généré / généré → GLB | 12,0 / 8,9 | 12,0 / 14,4 |
| Pièces arrondies retenues | 1 quart de rond 4×4 | **3 quarts de rond 4×4 + 1 coin arrondi 3×3** |

**Lecture.** Les écarts mesurés aux arcs étaient déjà faibles en V6 (moins de 12 LDU). À cette échelle, un coin carré reste près de l'arc, alors qu'il se voit nettement. C'est pourquoi la mesure aux extrémités (surface d'écart) et les rendus départagent les versions : `A_contours_bout.png`, `B_contours.png` et `gros_plans/`. L'IoU globale ne bouge presque pas, mais **les arrondis apparaissent** : coins carrés de V6 remplacés par des quarts de rond aux deux bouts du Beagle, marche et pointe de V6 remplacées par un arrondi au bout de Paco.

## 3. Vérifications

| | A : Paco (tête + oreille) | B : Beagle (oreille seule) |
|---|---|---|
| Collisions v3 / v2 | 0 / 0 | 0 / 0 |
| Pièces déconnectées / îlots / posées sans liaison | 0 / 0 / 0 | 0 / 0 / 0 |
| Notice | 78 étapes, 1 321 pièces, aucune retirée | 60 étapes, 276 pièces, aucune retirée |
| Oreille : références / pièces | 23 / 170 (au moins 82 sets par couple) | 30 / 276 (au moins 27 sets) |
| Couples pièce × couleur non vérifiés (modèle) | 0 | 0 |
| Masse de l'oreille | 75 à 83 g | 134 g (oreille de 20 tenons, âme pleine en hauteur) |
| Tenue indicative | Fixation V6 inchangée : 2 chemins (5 + 2 tenons), 2,13 N au bout dans le pire découpage. **Plaque supérieure visible.** | Pas de fixation : **non démontrée** |
| Silhouette globale face / profil (Paco) | 0,931 / 0,941 (V6 : 0,932 / 0,941) | — |

Hypothèses de tenue inchangées : 1 N par tenon (valeur supposée), pièces rigides, ce n'est pas une mesure. Aucun défaut visuel majeur n'apparaît ailleurs (`A_comparaison_V5_V6_V61.png`, `B_comparaison_V6_V61.png`).

## 4. Fichiers modifiés

- `generateur/autogen61.py` : nouveau, il ne remplace que l'étape de choix.
- `generateur/metrics61.py` : nouveau.
- `generateur/validate_v3.py` : nouvelle copie du validateur ; `validate_v2.py` n'est pas modifié.
- `generateur/autogen_V6_base.py` (= `proto/ear11/autogen.py`) : une seule ligne ajoutée, qui expose les pixels exclus (crâne, zones interdites) à V6.1. Elle ne change pas les résultats de V6.

Tous les résultats antérieurs (01 à 11) sont conservés.

**Aucune autre optimisation ni sculpture complète n'est commencée sans décision.**
