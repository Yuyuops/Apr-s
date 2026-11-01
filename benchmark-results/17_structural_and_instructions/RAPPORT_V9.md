# LEGO V9 : fiabiliser la sculpture et produire une vraie notice

Point de départ : commit `ce672d8` (V8.2). Le GLB source n'est pas modifié. Les dossiers 13 à 16 ne sont pas modifiés. Je n'ai rien acheté ni déployé, rien fusionné dans `main`, et je n'ai pas touché au moteur 2. Aucun essai physique n'a été fait.

## Verdict : **CORRIGER**

**Ce qui est obtenu :**

- un contrôle spatial automatique des modifications, avec des tests qui échouent sur V8.1 et réussissent sur V8.2 ;
- une sculpture dont les points faibles sont passés de **50 cas / 21 groupes à 17 cas / 8 groupes** (cas sous 0,5 N) par des renforts internes qui ne changent ni la silhouette ni les couleurs visibles ;
- un plan d'appui qui tient debout, ce qui n'était pas le cas ;
- une notice hiérarchique de **211 étapes** contrôlées une à une, au lieu de 326 étapes dont des oreilles posées d'un bloc.

**Le défaut précis qui empêche de valider :** le module d'oreille (V6.1, gelé par la consigne) contient **31 pièces (9 % des 346 pièces d'oreille) pour lesquelles le planificateur ne trouve aucune séquence d'assemblage** par translations rigides, et **deux groupes de bord d'oreille à risque élevé** n'ont pas pu être renforcés. Tout le reste du modèle (corps, bras, mains, détails du visage) est montable dans l'ordre de la notice selon les contrôles disponibles.

**Ce que ce verdict n'affirme pas :** je n'ai pas démontré que ces 31 pièces sont impossibles à monter, seulement que le modèle de mouvement du planificateur n'en trouve pas. Rien n'est démontré physiquement.

## 1. Défaut de V7 et V8 découvert : le plan d'appui

La statue V8.2 ne touche la table que par **4 plaques isolées** (3 de 1×1, 1 de 1×2 ; 45,4 cm² d'enveloppe) et le centre de gravité n'y est qu'à **4,2 mm** du bord de ce polygone : la statue basculerait au moindre effort. Le reste de la semelle est à 3,2 mm plus haut.

Mon rapport V7 annonçait « centre de gravité dans l'appui avec 74 mm de marge », calculé avec un appui approximatif. **Cette annonce était fausse pour le contact réel.**

**Correction R1** (`generateur/reinforce.py`) : les 4 plaques isolées (5 cellules, 3,2 mm) sont retirées. La statue repose alors sur **26 plaques, enveloppe de 132,2 cm², marge du centre de gravité de 41,1 mm**. Ce retrait modifie l'occupation de 5 cellules et rien d'autre ; il est déclaré, enregistré et contrôlé.

## 2. Contrôle de portée des modifications (`generateur/scope.py`, `tests/`)

**Principe.** Chaque module déclare la zone qu'il peut modifier (boîtes de cellules de 20 × 8 × 20 LDU). Deux modèles LDraw complets (avant, après) sont découpés en cellules à partir des vraies formes de pièces, puis comparés cellule par cellule :

| Catégorie | Violation hors zone ? |
|---|---|
| Occupation (cellule pleine dans un modèle, vide dans l'autre) | **Oui** |
| Couleur exposée (cellule qui touche l'extérieur) | **Oui** |
| Finition d'une face supérieure exposée (tenons ou tuile) | **Oui** |
| Couleur intérieure (cellule cachée) | Rapportée avec sa provenance, sans effet visuel |
| **Découpage seul** (même occupation, même couleur, autre répartition en pièces) | **Non** (compté) |
| Pièces hors réseau (oreilles, plaques tournées) | Comparées ligne à ligne (type, couleur, position, matrice) |

Chaque différence est rattachée aux zones qui la contiennent (provenance). Une zone « interface » explicitement déclarée peut recevoir une modification inattendue.

**10 tests sur 10 réussis** (`tests/resultats_tests.json`) :

| Test | Résultat |
|---|---|
| T1 Module V8.1 contre sa zone | **REJETÉ** : 153 cellules hors zone sur 245 |
| T2 Module V8.2 contre sa zone | **ACCEPTÉ** : 0 cellule hors zone sur 24 |
| T3a Modèle V8 → V8.1 | **REJETÉ** : 198 cellules de surface hors zone (dont 21 d'occupation) |
| T3b Entrées du moteur de volume V8 → V8.2 | Identiques hors zone (17 cellules différentes, toutes dans la zone) |
| T3c Modèle V8 → V8.2 | La dérive de reconstruction est **détectée** : 21 cellules de surface hors zone alors que les entrées sont identiques : dérive du moteur, pas du module |
| T4, T5 | Recoloration ou suppression d'une plaque lointaine : **REJETÉES** |
| T6 | Deux 1×1 remplacées par une 1×2 (même cellules, même couleur) : **pas une violation**, comptée comme découpage |
| T7 | Recoloration d'une plaque dans la zone déclarée : acceptée et attribuée au module |
| T8 | V8.2 → V9 : oreilles, yeux, truffe et pente rouge **identiques** (346 pièces : 337 d'oreille et 9 de détails ; positions et matrices) |

**Défaut de V8.2 que ce contrôle a trouvé :** la reconstruction du volume par le moteur a changé en silence la couleur de **21 cellules de surface** à la hauteur des épaules (rouge ↔ jaune), alors que les entrées du moteur ne différaient que dans la bouche. C'est la dérive de reconstruction. Elle est dans la référence V8.2 de V9 et **n'est pas corrigée** ici.

**V9 évite cette dérive par construction** : les renforts modifient directement la liste de pièces de V8.2, sans reconstruction globale. Résultat du contrôle V8.2 → V9 (`tests/scope_V82_V9.json`) :

| Mesure | Valeur |
|---|---|
| Violations hors zone | **0** |
| Occupation | 5 cellules (R1, plan d'appui) |
| Couleur exposée / finition de dessus | **0 / 0** |
| Couleur intérieure | 103 cellules, toutes dans les zones déclarées (cellules cachées recolorées) |
| Découpage seul | 1 444 cellules |
| Pièces hors réseau modifiées | 0 |

## 3. Diagnostic des 50 cas fragiles (21 groupes) de V8.2

**Définition** (celle de `validate_v3`) : un sous-ensemble de 1 g ou plus dont la force de décrochage indicative au bout est sous 0,5 N. Les cas emboîtés (même emplacement, plusieurs plans de coupe) sont regroupés : 50 cas → 46 distincts → **21 groupes**. La liste complète, avec positions, pièces, masses, liaisons, risque au montage et à la manipulation, est dans `rapport_avant_apres/points_faibles_V82.json`.

| Zone | Groupes | Pièces | Masse | Force indicative | Catégorie |
|---|---|---|---|---|---|
| **Cas de tout le modèle** (n° 1) | 1 | 2 752 | 1 118 g | 0,17 N sur **5 tenons** | **Plan d'appui** : les 4 plaques de la semelle (voir § 1) |
| Jambes (colonnes de rouge, 6 groupes) | 6 | 7 à 30 | 1,2 à 12,2 g | 0,07 à 0,47 N | Décoration (1 colonne de 10 plaques tenue par 1 tenon) à structurel (30 pièces, 7 tenons) |
| Bords d'oreille | 4 | 5 à 18 | 1,3 à 8,1 g | 0,08 à 0,41 N | Structurels et exposés : **risque élevé** pour 2 groupes |
| Mains et doigts | 3 | 5 à 21 | 1,2 à 5,2 g | 0,22 à 0,34 N | Décoration à structurel |
| Visage (museau, côté de l'œil) | 3 | 7 à 10 | 1,1 à 1,3 g | 0,07 à 0,29 N | Décoration légère |
| Torse | 2 | 7 à 8 | 1,0 à 1,1 g | 0,26 N | Décoration légère |
| Semelles et bas de jambes | 2 | 5 | 1,4 g | 0,39 N | Décoration légère |

Je n'ai **pas** traité tous les groupes à un tenon de la même manière : une colonne décorative de 1,6 g (poids propre 0,016 N, résistance de 1 N par tenon) n'est pas un sous-ensemble structurel de 8 g à un tenon exposé à la main.

## 4. Renforts (`generateur/reinforce.py`)

Les renforts utilisent **uniquement de vraies liaisons** (tenons engagés dans des cavités, comptées par la même géométrie que `validate_v3`) et ne modifient que des plaques droites 1×N sur le réseau. Les tuiles, pentes, ailes et pièces d'oreille ne sont pas touchées.

**R2, ponts internes.** Pour un groupe fragile, on examine les cellules voisines dans la même couche de plaque. Une cellule voisine rejoint la région du groupe si :

- elle porte une plaque de la même couleur (simple recoupage), ou
- elle est **cachée** (ses six faces touchent des cellules occupées) : on lui donne la couleur du groupe, sans effet visible.

On choisit les cellules par le gain réel de liaisons (cellule au-dessus ou au-dessous appartenant à une autre pièce, la pièce du bas portant des tenons), couche par couche. La région est ensuite recoupée en plaques disponibles de la couleur, **avec au moins une plaque à cheval entre le groupe et la cellule ajoutée** : deux plaques seulement côte à côte ne forment pas une liaison. Le premier essai, sans cette règle, n'avait pas amélioré les groupes.

**Garde-fou de connectivité.** Après chaque groupe, le graphe de joints du modèle est recalculé ; si une pièce n'est plus reliée au plan d'appui, le groupe est annulé. Cela est arrivé : 4 groupes ont été annulés parce qu'une plaque qui faisait pont entre deux colonnes avait été coupée.

| Passe | Groupes traités | Appliqués | Annulés (connectivité) | Sans cellule utilisable | Cellules ajoutées |
|---|---|---|---|---|---|
| 1 | 16 | 14 | 2 | 0 | 177 |
| 2 | 5 | 2 | 2 | 1 | 52 |

**Résultat** (`validate_v3`, V8.2 → V9) :

| Mesure | V8.2 | V9 |
|---|---|---|
| Pièces / types | 2 756 / 42 | 3 066 / 42 |
| Cas sous 0,5 N | **50** | **17** |
| Cas sous 2 N | 131 | 77 |
| Force minimale | 0,07 N | 0,08 N |
| Groupes fragiles | 21 | **8** |
| Collisions / déconnectées / îlots | 0 / 0 / 0 | 0 / 0 / 0 |
| Masse | 1 118 g | 1 118 g |
| Plan d'appui | 4 plaques, 45,4 cm², marge 4,2 mm | 26 plaques, 132,2 cm², marge 41,1 mm |

Le coût est de **+310 petites plaques** (+11 %), toutes de références déjà utilisées : le catalogue garde 73 couples pièce × couleur, **tous vérifiés**, aucune nouvelle référence.

**Rendu.** Aux mêmes vues et à la même lumière, moins de 0,4 % des pixels du personnage entier diffèrent entre V8.2 et V9, et moins de 0,07 % sur les gros plans de la tête : la différence se limite aux points sombres des semelles qui disparaissent.

## 5. Les 8 groupes qui restent (`rapport_avant_apres/points_faibles_V9.md`)

| Zone | Groupes | Pièces / masse | Tenons / force | Pourquoi ils restent |
|---|---|---|---|---|
| Bord d'oreille | 4 | 15 p 5,1 g ; 7 p 3,5 g ; 5 p 1,3 g ; 18 p 8,1 g | 1 / 0,08 N ; 1 / 0,21 N ; 1 / 0,27 N ; 3 / 0,41 N | Pièces du module d'oreille (gelé) ; leurs voisines sont des pièces de contour, pas des cellules cachées |
| Mains | 2 | 5 p 1,0 g ; 12 p 2,1 g | 2 / 0,26 N ; 3 / 0,26 N | Doigts de 1 cellule de large : aucune cellule cachée autour |
| Museau | 2 | 7 p 1,3 g ; 9 p 1,4 g | 2 / 0,19 N ; 3 / 0,26 N | Bout du museau très fin ; pas de cellules cachées |

**Risque.**

- **Élevé :** les groupes d'oreille de 15 et 7 pièces (structurels, exposés à la main, 3,5 à 5 g).
- **Moyen :** les mains (manipulables).
- **Faible :** les bouts de museau (légers, décoratifs).

Ces risques sont qualitatifs et fondés sur le modèle indicatif ; ils sont à confirmer par l'essai du protocole.

## 6. Limites du modèle de résistance

Le calcul reste celui de `validate_v3`, sans changement. **Je n'ai pas touché au modèle pour améliorer les résultats.**

- **1 N par tenon, supposé.** Les valeurs mesurées sur des briques neuves vont d'environ 1 à 4 N et baissent avec l'usure, le lot de couleur et la température.
- **Pièces rigides, aucune souplesse** des tenons ni des plaques.
- **Compression gratuite.** Aucun écrasement.
- **Un seul sens de coupe par plan** : la direction dominante des liaisons ; les autres sont ignorées (conservateur).
- **Efforts de cisaillement non modélisés** : une pièce qui glisse latéralement sur ses tenons n'est pas considérée comme décrochée.
- **Moment de flexion limité** au pivotement autour de l'arête du polygone de tenons.
- **Frottement entre pièces voisines et jeu** ignorés.
- **Plusieurs cas peuvent se recouvrir** (un sous-ensemble plus grand contient un plus petit) : le décompte « cas » n'est pas un décompte de zones distinctes (d'où les « groupes »).

## 7. Notice (`notice/`)

Voir `RAPPORT_NOTICE.md`.

## 8. Contrôles globaux de V9

| Contrôle | Résultat |
|---|---|
| `validate_v3` sur la notice ordonnée | 3 066 pièces, 211 étapes, **0 collision, 0 déconnectée, 0 îlot**, 0 sous-ensemble non attachable ; 18 « non soutenues à la pose » = pièces posées sur un appui sans emboîtement ou premières pièces d'une unité d'oreille |
| Collisions non autorisées | **0** |
| Disponibilité | 73 couples pièce × couleur, **tous vérifiés** (Rebrickable, au moins 20 sets) |
| Centre de gravité | 189,5 mm de haut ; dans le plan d'appui avec **41,1 mm** de marge (plan de 26 plaques) |
| Contrôle de portée V8.2 → V9 | **0 violation** |
| Non-régression visage et oreilles | Pièces identiques : yeux, truffe, pente rouge, 337 pièces d'oreille (T8) |
| Non-régression V6 / V6.1 | **Rejouée** depuis les entrées archivées : modèles, rapports, validations et nomenclatures **identiques** aux références (`tests/nonreg_V6_V61.json`) |
| Accessibilité (corps, bras, mains, détails) | Toutes les pièces sont insérables selon le planificateur ; 9 pièces demandent un chemin avec virages |
| Accessibilité (oreilles) | **31 pièces sans séquence trouvée** (14 étapes avec alerte) ; accrochage des deux oreilles sur la tête possible à leur plus tôt |
