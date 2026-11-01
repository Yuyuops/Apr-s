# Protocole d'essai physique minimal : fixations des oreilles (V7)

**Rien n'est acheté et rien n'est commandé.** Ce protocole ne sera exécuté qu'avec l'accord de l'utilisateur, et seulement avec des pièces déjà disponibles.

## Bancs (`bancs_essai/`)

Chaque banc est tiré automatiquement du modèle V7 (`code/rig_v7.py`) :

- mêmes plaques tournées, même bloc de racine, mêmes appuis 1×1, aux **mêmes coïncidences 3-4-5** que dans la sculpture ;
- la tête est remplacée par une plaque de base grise et des colonnes de 1×1 ;
- les appuis testés sont en **rouge** ;
- un levier jaune 4282 (2×16) est fixé sur la plaque tournée la plus haute, dirigé vers le bout de l'oreille.

| Banc | Pièces | Base | Liaisons testées | Plaque 1 | Plaque 2 | Validation |
|---|---|---|---|---|---|---|
| `banc_oreille_haute.ldr` | 18 | 3036 (6×8) | 6 | 3034 2×8, 4 appuis | 3031 4×4, 2 appuis | 0 collision, 0 déconnectée |
| `banc_oreille_basse.ldr` | 34 | 91405 (16×16) | 12 | 3035 4×8, 7 appuis | 3035 4×8, 5 appuis | 0 collision, 0 déconnectée |

Nomenclatures : `bancs_essai/nomenclature_banc_*.csv` (pièces courantes, toutes vérifiées sur Rebrickable).

## Mesures

1. Monter le banc et vérifier que la plaque tournée **s'emboîte sans forcer** sur les appuis rouges. Noter **oui / non**, ainsi que le jeu ressenti.
2. Accrocher des masses au bout du levier, à environ **124 mm** de la racine : 20 g, puis 50 g, 100 g, 200 g, et ainsi de suite jusqu'au décrochage. **3 essais par banc**, en remontant les pièces à chaque fois.
3. Noter la masse de décrochage, la liaison qui lâche en premier (chemin 1 ou chemin 2), et si l'autre chemin retient l'oreille.
4. Recommencer le test 2 en chargeant le levier **vers le haut** (simulation d'une prise en main).

## Critères

| Critère | Seuil |
|---|---|
| Emboîtement | Sans forcer, à chaque appui |
| Tenue sous le poids propre | Moment à rupture ≥ **3 ×** le moment de l'oreille. Oreille basse : 59 g, centre de masse à environ 60 mm, soit environ 35 mN·m. **Il faut donc au moins 90 g au bout du levier.** |
| Manipulation | Au moins 0,5 N au bout de l'oreille, soit environ **100 g au levier**, sans décrochage |
| Redondance | Le chemin restant retient l'oreille après la rupture du premier |

Si un critère n'est pas atteint, la correction minimale serait l'une des suivantes :

- relever d'un niveau la plaque secondaire (v + 40), ce qui donne plus d'appuis ;
- passer la plaque principale de 2×8 à 4×8 ;

puis relancer la recherche automatique.

**Les valeurs calculées sont indicatives** (1 N par tenon supposé). **Seul cet essai validera les fixations.**
