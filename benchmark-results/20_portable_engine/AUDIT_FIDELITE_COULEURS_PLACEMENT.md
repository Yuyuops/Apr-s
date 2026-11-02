# Audit de fidélité : couleurs et placement (GLB source / pièces LEGO)

**Aucune couleur ni position n'a été modifiée en V11.** Cet audit est un diagnostic ; les corrections sont renvoyées à la mission suivante. Outil : `engine/audit_fidelity.py` ; modèles audités : les références historiques **Paco V9.1** (`18_ear_assembly_final/modeles/paco_V91_brut.ldr`) et **Beagle V10** (`19_full_second_subject/modeles/beagle_V10_brut.ldr`) ; rapports complets et cartes : `audit/`. Tests automatiques : `tests/run_tests.py` (T5 à T7, 9/9).

## 1. Méthode

* **Rien n'est lu sur un rendu** : l'audit compare la couleur des **vraies pièces** (cellules exposées du modèle assemblé, 20 × 8 × 20 ldu, voisines de l'extérieur) à la couleur de la surface du GLB autour d'elles (moyenne des 10 sommets les plus proches, dans 24 ldu = 9,6 mm), en écart ΔE CIE76 dans l'espace Lab. **Les joints, les ombres et l'éclairage d'un rendu ne peuvent donc pas être comptés comme des défauts** ; à l'inverse, une couleur de rendu trompeuse ne peut pas masquer une pièce mal colorée.
* **Plancher** : le plus petit ΔE atteignable avec (a) les couleurs que le **quantificateur du moteur** a gardées pour ce sujet (palette du moteur), (b) tout le **catalogue autorisé** (couleurs LDraw opaques non exclues et vendues en plaque 1×1 dans au moins 20 sets Rebrickable). **Excès** = ΔE − plancher du moteur : la part de l'erreur que la palette du moteur aurait pu éviter.
* **Brique parasite** : cellule exposée dont l'excès est d'au moins 40 (seuil d'audit, pas un paramètre du moteur). **Sans correspondance** : échantillon du GLB dont le plancher du catalogue est d'au moins 30.
* **Module responsable** : par type de pièce (oreilles, détails du visage) et, avec le dossier de run, par comparaison des grilles intermédiaires (palette, assemblage V8, module de bouche, reconstruction).
* **Placement** : IoU d'occupation par zone (occupation fine du GLB contre le modèle) ; oreilles (centre, normale, asymétrie par rapport au plan sagittal) ; taches du GLB (yeux, truffe, bouche) contre les pièces de détail construites ; pièces structurelles visibles.

## 2. Résultats d'ensemble

| | Paco V9.1 | Beagle V10 |
|---|---:|---:|
| Cellules exposées / avec surface GLB | 6 212 / 5 929 | 11 846 / 11 846 |
| ΔE moyen (médian) | **20,4** (12,9) | **17,1** (15,6) |
| Plancher palette du moteur / catalogue | 14,6 / 14,2 | 14,3 / 12,4 |
| Excès moyen | 5,8 | 2,8 |
| **Cellules parasites** (excès ≥ 40) | **369 (6,2 %)** | **195 (1,7 %)** |
| Cellules sans correspondance au catalogue | **467** | 0 |
| IoU d'occupation global | 0,867 | 0,998 |
| Pièces structurelles visibles (SNOT) | 5 cellules (87087) | 0 |

**Correction d'une affirmation de V10.** Le rapport V10 donnait « écart de couleur d'environ 100 sur 255 » entre le GLB et le LEGO. Cette valeur venait de la **moyenne des pixels des rendus** (éclairage, ombres et joints compris), qui n'est pas la couleur des pièces. Mesurée sur les pièces, l'erreur du Beagle est un **ΔE moyen de 17,1** (plancher 14,3), du même ordre que celle de Paco (20,4). Le Beagle est donc moins sombre que V10 ne le disait ; ses défauts de couleur sont localisés (§ 3). Les fichiers de V10 ne sont pas modifiés ; cette correction vit ici.

## 3. Cartographie des défauts

Cartes de l'excès (vert = nul, rouge = 60 ou plus ; contour noir = parasite) : `audit/carte_defauts_couleur_{paco,beagle}_{face_XY,profil_ZY,dessus_XZ}.png`.

### Paco

| # | Défaut | Mesure | Gravité | Module responsable |
|---|---|---|---|---|
| P1 | **Briques noires dans des surfaces jaunes** (et rouges) | 237 cellules noires parasites ; attendu jaune 218, rouge 10, blanc 9 ; zones : crâne 106, museau 57, hors zone 55, jambes 10 ; types : plaques de fixation 3035, 3034, 3008, 3007, 3031 (**106 cellules de pièces d'oreille exposées**), plaques 3024 et 3023 du volume | **Majeure** (visible, 3,8 % des cellules exposées) | **Module d'oreille** : la plaque principale 2×8, la plaque secondaire et le bloc de racine sont noirs et affleurent la surface du crâne, contrairement à la règle de V7 (« la plaque tournée qui atteint la surface prend la couleur de la surface ») ; **reconstruction brickify_plus** pour les 120 autres (pièces du volume noircies par la quantification autour des oreilles) |
| P2 | **Confusions rouge / jaune** | rouge attendu, jaune construit 92 ; jaune attendu, rouge 77 | Moyenne | Palette brickify et reconstruction : frontières de couleur de la salopette ; 169 cellules parasites du volume attribuées à la reconstruction et aux ponts de renfort |
| P3 | **Tons sans correspondance** (ocre, brun, orangé du GLB) | 467 cellules : GLB (201,124,23) 127 cellules, (178,139,67) 94, (148,103,23) 93, (124,55,43) 153 ; meilleur du catalogue : jaune ou rouge, écart 38 à 50 | Moyenne | **Palette** : quatre couleurs de référence imposées ; le catalogue n'a pas mieux parmi les couleurs non exclues |
| P4 | Yeux et détails de la bouche | 2 yeux et 2 pupilles construits à 1,8 à 7,8 mm des taches du GLB ; 3 taches de bouche détectées : 1 pièce à 6,6 mm, 2 non construites (31 et 50 mm) ; « œil douteux » et pupille douteuse rejetés | Faible | Détection V8 / module de bouche |
| P5 | **Oreilles : centre** | basse : écart de centre 17,6 mm, normale à 4,3° ; haute : 11,1 mm, 0,8° | Faible (orientation bonne) | Générateur d'oreilles. **Limite de la mesure** : le nuage du GLB est la partie sombre de la zone de l'oreille, celui du LEGO comprend les plaques de fixation noyées dans la tête : l'écart de centre est un majorant, pas une erreur propre. Les étendues ne sont donc pas comparables (mesurées, non interprétées) |
| P6 | **Oreilles : asymétrie** | différence de hauteur entre les deux oreilles : GLB 87,7 mm, LEGO 98,0 mm ; somme des distances au plan sagittal : GLB 45,6 mm, LEGO 36,5 mm | Faible | **L'asymétrie est dans la source** (87,7 mm de dénivelé entre les deux oreilles du GLB) ; le générateur y ajoute environ **10 mm** (hauteur) et **9 mm** (plan) |
| P7 | Pièce structurelle visible | 5 cellules de brique à tenon latéral 87087 (support de la truffe) exposées | Faible | Module de détails (truffe) |
| P8 | Volume | IoU 0,867 ; oreille haute 0,847, basse 0,921, yeux 0,5 (14 cellules) ; jambes, torse, bras 1,0 | Faible | Voxélisation + oreilles remplacées par le module |

### Beagle

| # | Défaut | Mesure | Gravité | Module responsable |
|---|---|---|---|---|
| B1 | **Briques jaunes et rouges parasites** | **51 jaunes, 15 rouges**, noires 26 (surtout crâne et museau) : le jaune (14) et le rouge (4) **n'existent pas dans la palette du Beagle** (grille : noir, blanc, Reddish Brown, Medium Nougat, Dark Brown, Dark Orange) | **Majeure** (couleurs absentes du chien) | **Détails du visage V8 / module de bouche** : les classes de taches (« noir, jaune, rouge, blanc ») sont les couleurs de Paco, câblées dans `detect.py`, `microdetails.py` et `lcm82.py` : 39 cellules du module de bouche, 12 des micro-détails, 10 de l'assemblage V8 ; les autres sont des plaques recoloriées du volume. 106 plaques jaunes ou rouges au total dans la nomenclature |
| B2 | **Confusions de teintes brunes** | Medium Nougat attendu, White construit 419 ; Medium Nougat → Dark Orange 296 ; White → Medium Nougat 242 ; Dark Orange → Medium Nougat 232 ; Reddish Brown ↔ Dark Brown 244 | Moyenne (≈ 12 % des cellules ont une teinte voisine mais fausse) | **Palette brickify** (quantificateur, 4 passes) et bruit de frontière |
| B3 | **Yeux non détectés, donc non construits** | aucune tache « œil » dans le GLB analysé ; zone « yeux » de la segmentation = 192 cellules, IoU 0,975 (le blanc des pattes), sans signification | **Majeure** (le chien n'a pas de regard) | **Segmentation et détection** : règles de Paco (œil = tache blanche à pupille noire) |
| B4 | **Oreilles dans le volume** | pas de module ; zone « crâne » IoU 0,999 ; 13 cellules noires et 13 rouges dans le crâne | Majeure (forme) / faible (occupation) | Absence de module d'oreille générique |
| B5 | **Taches de « bouche » erronées** | 20 taches « bouche » détectées (noir et rouge), 1 seule à moins de 2 mm d'une pièce de détail ; la truffe est construite à 4,4 mm | Moyenne | Détection de bouche de Paco appliquée à la langue et aux plis du Beagle |
| B6 | Pas de rose | le rose (langue, truffe) n'est pas dans la palette du moteur (plancher moteur 14,3 contre 12,4 au catalogue) | Faible | Palette |
| B7 | Volume | IoU 0,998 ; yeux 0,975, truffe 0,826 | Nul à faible | Voxélisation |

## 4. Origine par module (cellules parasites)

| Module | Paco | Beagle |
|---|---:|---:|
| Reconstruction brickify_plus et ponts de renfort | 169 | 111 |
| Générateur d'oreilles | 106 | — |
| Palette brickify (quantificateur) | 66 | 23 |
| Micro-détails et module de bouche (lcm82 compris) | 25 | 51 (dont lcm82 : 39) |
| Assemblage V8 | 3 | 10 |

## 5. Corrections nécessaires (non faites)

1. **Couleurs des classes de détails par sujet** : remplacer les noms de classes (noir, jaune, rouge, blanc) de `detect.py`, `microdetails.py`, `lcm82.py` par une correspondance de la configuration du sujet vers sa palette (supprime B1 et B5).
2. **Plaques de fixation des oreilles de Paco** : appliquer la règle de V7 (couleur de la surface remplacée, tuile de cette couleur sur les tenons libres) à toutes les plaques exposées (P1, 106 cellules).
3. **Palette** : sélection par minimisation de l'écart de couleur sur l'ensemble du catalogue autorisé, et inclusion des couleurs de référence du sujet (rose du Beagle) ; réduction des confusions de frontière (P2, P3, B2, B6).
4. **Détection d'yeux et d'oreilles indépendante de la palette** (B3, B4) : interfaces dans `ARCHITECTURE.md` § 5.
5. **Mesure d'oreille** : comparer des nuages de même définition (surface visible du LEGO seule) pour supprimer le biais du point P5.

## 6. Tests automatiques

`tests/run_tests.py` : **T5** l'audit des deux références retrouve les défauts de la baseline archivée (`refs/audit_baseline.json` : Paco 369 parasites, 467 sans correspondance, ΔE 20,4, IoU 0,867 ; Beagle 195, 0, 17,1, 0,998) ; **T6** 60 plaques Dark Orange du Beagle recoloriées en bleu sont détectées (+73 cellules parasites) ; **T7** l'oreille haute de Paco déplacée de 32 mm est détectée (écart de centre 11,1 → 35,2 mm). Après chaque régénération, `T5` doit retrouver ces défauts tant qu'ils ne sont pas corrigés (ils sont la référence de diagnostic).

**Limites de l'audit** : le seuil de 40 sur l'excès ne compte que les défauts francs ; les erreurs modérées sont dans l'excès moyen ; la résolution est celle d'une cellule (20 × 8 × 20 ldu) ; l'échantillonnage du GLB suppose que la surface la plus proche est la bonne (zones fines, pattes, doigts) ; l'attribution fine d'un module exige le dossier du run.
