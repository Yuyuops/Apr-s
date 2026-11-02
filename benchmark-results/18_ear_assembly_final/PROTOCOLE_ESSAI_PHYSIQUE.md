# Protocole d'essai physique minimal : oreilles renforcées, montage, points faibles (V9.1)

**Aucun essai physique n'a été réalisé. Aucun achat n'est fait ni demandé.** Ce protocole n'est exécuté qu'avec l'accord de l'utilisateur, avec des pièces déjà disponibles. Tout ce que les rapports disent de la résistance reste **indicatif et non démontré physiquement**.

## 1. Les deux bancs de fixation d'oreille (V7), toujours valables

Les pièces de fixation des oreilles (plaque principale 2×8, plaque secondaire cachée, bloc de racine, briques de racine) sont **identiques** en V7, V8, V9 et V9.1 (mêmes références, positions, matrices : `validation/checks_v91.json`). Seules des **tuiles de face** ont changé. Les bancs de V7 restent donc valables (`bancs_essai/`) :

| Banc | Fichier | Contenu |
|---|---|---|
| Oreille haute | `banc_oreille_haute.ldr` | 6 liaisons testées, base 6×8, levier 4282 (2×16) |
| Oreille basse | `banc_oreille_basse.ldr` | 12 liaisons testées, base 16×16, levier 4282 (2×16) |

Liste minimale des pièces des bancs : `bancs_essai/liste_pieces_minimale_bancs.csv` (11 références, 38 pièces ; 52 pièces pour les deux bancs ensemble).

## 2. Ce qu'il faut éprouver en V9.1, sur la sculpture montée

Rien à acheter : un dynamomètre ou des masses marquées, un fil fin, une balance.

| Essai | Objet | Mesure |
|---|---|---|
| **A. Montage selon la notice** | Les 5 PDF, dans l'ordre ; deux personnes ne connaissant pas les rapports si possible | Pour **chaque étape** : faisable oui/non, effort inhabituel, étape où il faut tenir, étape impossible. Noter surtout les 57 poses par le dessous de l'oreille basse, les 55 poses de bras, les 8 premières étapes de l'oreille basse |
| **B. Bord d'oreille, traction** | Les calottes de bord de l'oreille basse (haut-droite, bas, coin gauche) : zones renforcées par 18 tuiles à cheval | Fil fixé à la calotte, effort perpendiculaire à l'oreille, puis dans le plan (cisaillement). Noter la force au décrochage et la pièce qui lâche en premier |
| **C. Bord d'oreille, comparaison** | Idem sans les tuiles à cheval (modèle V9 : tuiles d'origine) si l'on a les pièces | Même mesure : le gain réel du renfort |
| **D. Bancs de fixation** | Banc haut et banc bas, masses à environ 124 mm de la racine par paliers de 20, 50, 100, 200 g, 3 essais par banc | Masse de décrochage et liaison qui lâche |
| **E. Mains et museau** | Les 4 groupes non renforcés (main droite 2,1 g en particulier) | Effort sur le bout, jusqu'au décrochage |
| **F. Manipulation** | Soulever la sculpture par le torse, puis par la tête, 5 fois chacune | Tout détachement (pieds, oreilles, mains, museau) |
| **G. Poids propre** | Sculpture debout, 10 minutes | Glissement ou décrochage |
| **H. Stabilité debout** | Incliner doucement la sculpture (mesure de l'angle de basculement) | À comparer à la marge calculée de 41,1 mm du centre de gravité |
| **I. Pesée** | Peser la sculpture montée et, si possible, un échantillon de chaque référence (1×1, 1×2, 1×6, 2×4, tuile 1×2…) | Masse réelle ; à comparer aux 1 117,7 g du modèle |

## 3. Procédure (chaque liaison ou groupe)

1. **Montage** : suivre la notice. Noter pour chaque pièce l'effort d'emboîtement et l'ordre non réalisable.
2. **Poids propre** : 10 minutes en position normale.
3. **Effort au bout du levier** (bancs) : masses accrochées à environ 124 mm de la racine.
4. **Effort sur la sculpture** (essais B, C, E) : traction progressive par dynamomètre ou masses.
5. Noter la force ou la masse de décrochage, la liaison qui lâche en premier, si un autre chemin retient la pièce.

## 4. Critères

| Critère | Seuil |
|---|---|
| Montage | Chaque étape de la notice faisable ; toute étape non faisable est un défaut de la notice |
| Poids propre | Aucun glissement en 10 min |
| Bout de l'oreille (bancs) | Au moins 3 fois le moment de l'oreille : oreille basse 59 g, centre de masse à environ 60 mm, soit au moins 90 g au bout du levier |
| Manipulation normale | Au moins **0,5 N** (environ 50 g) au bout d'un bord d'oreille, d'une main ou du museau, sans décrochage |
| Soulèvement | La sculpture se lève par le torse et par la tête sans que rien ne se détache |
| Stabilité | Angle de basculement cohérent avec la marge de 41 mm (à noter ; pas de seuil fixé) |

## 5. Ce qui reste non démontré physiquement

* **La tenue des calottes de bord d'oreille renforcées** : le modèle de calcul suppose 1 N par tenon, des pièces rigides, aucun frottement, aucun jeu, et **ignore le cisaillement**, que subissent les tenons des tuiles à cheval.
* **Les 4 groupes non renforcés** (mains, museau).
* **Le montage lui-même** : accessibilité des doigts, forces d'emboîtement, étapes à tenir à la main, tolérances des tenons, souplesse des pièces.
* **La stabilité debout**, la **masse réelle** de la sculpture.
* **L'indépendance mécanique des deux chemins de fixation** de chaque oreille.
