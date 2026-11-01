# Protocole d'essai physique minimal : fixations et points faibles (V9)

**Aucun essai physique n'a été réalisé. Aucun achat n'est fait ni demandé.** Ce protocole n'est exécuté qu'avec l'accord de l'utilisateur, avec des pièces déjà disponibles. Tout ce qui est écrit dans les rapports sur la résistance reste **indicatif et non démontré physiquement**.

## 1. Les deux bancs de fixation d'oreille (V7, inchangés)

Les oreilles de V9 sont **identiques** à celles de V7 et V8 (mêmes pièces, mêmes positions, mêmes matrices : test T8). Les bancs de V7 restent donc valables. Ils sont copiés ici (`bancs_essai/`) :

| Banc | Fichier | Contenu |
|---|---|---|
| Oreille haute | `banc_oreille_haute.ldr` | 6 liaisons testées, base 6×8, levier 4282 (2×16) |
| Oreille basse | `banc_oreille_basse.ldr` | 12 liaisons testées, base 16×16, levier 4282 (2×16) |

Chaque banc reproduit les plaques tournées de la fixation, leur bloc de racine et leurs appuis 1×1, aux mêmes coïncidences 3-4-5. La tête est remplacée par une plaque de base et des colonnes de briques.

**Liste minimale des pièces** (un banc à la fois, on reconstruit entre deux essais) : `liste_pieces_minimale_bancs.csv`, soit 11 références et 38 pièces. Si l'on monte les deux bancs en même temps, il faut 52 pièces (nomenclatures séparées).

## 2. Essai des points faibles résiduels, sans pièce supplémentaire

Les 8 groupes fragiles qui restent (`rapport_avant_apres/points_faibles_V9.md`) sont éprouvés **sur la sculpture montée**, avec seulement un dynamomètre ou des masses marquées et un fil fin. Rien à acheter.

| Banc d'essai | Groupes concernés | Mesure |
|---|---|---|
| Bords d'oreille (4 groupes, dont 2 à risque élevé) | n° 1, 5, 6, 8 | Fil fixé au bout du groupe, effort perpendiculaire à l'oreille |
| Mains et doigts (2 groupes) | n° 2, 7 | Effort sur le bout de la main |
| Museau (2 groupes) | n° 3, 4 | Effort sur le bout du museau |

## 3. Procédure (pour chaque liaison ou groupe)

1. **Montage** : suivre la notice. Noter, pour chaque pièce, si l'emboîtement a demandé un effort inhabituel, et les pièces du groupe qui n'ont pas pu être posées dans l'ordre prévu.
2. **Poids propre** : poser le banc ou la sculpture dans sa position normale pendant 10 minutes. Noter tout glissement ou décrochage.
3. **Effort au bout du levier** (bancs) : accrocher des masses à environ **124 mm** de la racine, par paliers de 20, 50, 100, 200 g, jusqu'au décrochage. **3 essais par banc**, en remontant les pièces à chaque fois.
4. **Effort sur la sculpture** : tirer doucement, avec un dynamomètre ou des masses, perpendiculairement au groupe testé. Noter la force au décrochage.
5. **Manipulation** : soulever la sculpture par le torse, puis par la tête, 5 fois chacune, sur une table. Noter tout détachement (pieds, oreilles, mains, museau).
6. Noter la masse ou la force de décrochage, la liaison qui lâche en premier, et si un deuxième chemin retient la pièce.

## 4. Critères

| Critère | Seuil |
|---|---|
| Emboîtement | Sans forcer, à chaque appui. Aucune pièce de la notice qui ne puisse être posée |
| Poids propre | Aucun glissement en 10 min |
| Bout de l'oreille | Au moins 3 fois le moment de l'oreille : oreille basse, 59 g, centre de masse à environ 60 mm, soit au moins 90 g au bout du levier |
| Manipulation normale | Au moins 0,5 N au bout d'un bord d'oreille, d'une main ou du museau, soit environ 50 g, sans décrochage |
| Soulèvement | La sculpture se lève par le torse et par la tête sans que rien ne se détache |

## 5. Ce qui reste non démontré physiquement

- **La tenue des 8 groupes résiduels.** Le modèle de calcul suppose 1 N par tenon, des pièces rigides, aucun frottement entre pièces voisines ni jeu, et ne considère que les efforts de traction et le moment autour de l'arête de la zone de contact. Il ignore le cisaillement, la torsion, la fatigue et l'usure.
- **Les 31 pièces d'oreille sans séquence d'assemblage** trouvée par le planificateur. Ce n'est pas une preuve d'impossibilité. Elle doit être jugée par un essai de montage.
- **L'accessibilité réelle à la main** : le planificateur ne contrôle que des translations rigides et des chemins en ligne droite ou avec virages. Il ne tient pas compte des doigts, des outils ni de la souplesse des pièces.
- **La stabilité de la statue debout** : le plan d'appui (26 plaques, 132 cm², marge du centre de gravité de 41 mm) est calculé, pas mesuré.
