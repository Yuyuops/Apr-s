# Cause racine de la régression mécanique V12 (Beagle 10 → 32 cas < 0,5 N, FS gravité 38,2 → 15,8)

Méthode : toutes les mesures utilisent le même validateur (`validate_v4.py` + `weak_groups.py`), les mêmes seuils (0,5 N / 2 N, 1 g, 1 N par tenon) et la même base Rebrickable de référence (`LEGO_DEPS`). Le Beagle V11 (archive V10) a été **revalidé avec cette méthode** : 10 cas, FS 38,23, force de bout minimale 0,10 N, c'est-à-dire exactement les valeurs archivées. Aucun seuil ni coefficient de tenue n'a été modifié.

## 1. Ce qui a changé, étape par étape (Beagle)
| Variante (même sujet, même GLB) | pièces | cas < 0,5 N | groupes | FS gravité min | force de bout min |
|---|---|---|---|---|---|
| V11 (archive V10, modules de détail câblés Paco) | 11 111 | 10 | 7 | 38,23 | 0,10 N |
| a. modules sans couleurs de Paco, palette V11 figée, renfort historique | 11 147 | **22** | 7 | 38,23 | 0,05 N |
| b. + palette automatique (= V12), renfort historique | 10 498 | **32** | 7 | 15,79 | 0,06 N |
| c. palette V11 figée + renfort V12.1 | 11 153 | 4 | 4 | 38,23 | 0,31 N |
| d. palette automatique + renfort V12.1 (**V12.1, rejeu complet**) | 10 567 | **0** | 0 | **43,25** | **0,52 N** |
Étapes intermédiaires (mêmes méthodes) : avant tout renfort (`v82`) 155 cas (a) et 148 cas (b) ; après la passe 1 : 41 et 41 ; après la passe 2 : 22 et 32.

Lecture :
* **Le changement de palette ne fragmente pas davantage la structure de départ** (148 cas contre 155 avant renfort ; 41 contre 41 après la passe 1). La régression naît **dans le renforcement**.
* **La réparation de couleur n'y est pour rien** : elle ne change que des codes couleur ; 32 cas avant et 32 cas après (journal `pass2` → `final`), géométrie identique.
* **La génération des plaques** change (−613 pièces, −3,3 % de liaisons par rapport à V11) mais n'ajoute pas de point faible par elle-même (cf. ligne c : même renfort, 4 cas).

## 2. Les groupes réellement nouveaux et les liaisons perdues
Sept groupes fragiles en V11, sept en V12, mais **trois nouveaux** en V12 (position en LDU) :
| groupe V12 | pièces | tenons | force | cas emboîtés | région / fonction | pourquoi il subsiste |
|---|---|---|---|---|---|---|
| [220..240, −248..−8, 620..900] Dark_Tan + blanc | **69** | **3** | 0,15 N | **24** | paroi externe d'une patte (zones pieds 93 cellules, jambes 78 ; feuille d'une cellule d'épaisseur, couche externe) | **`reinforce.py` ignore tout groupe de plus de 60 pièces** (« cas du modèle entier », réservé à la règle R1). Ce groupe de 69 pièces n'a jamais été examiné : 24 des 32 cas viennent de lui |
| [460..480, −880..−784, 740..760] Noir + Reddish_Brown | 12 | 1 | 0,06 N | 3 | crâne (52 cellules) | tentatives de pont annulées (« une liaison entre colonnes coupée ») : la retuilisation d'une cellule voisine coupait un lien existant |
| [120..160, −968..−928, 900..940] Noir + Dark_Orange | 8 | 2 | 0,26 N | 1 | crâne | idem |
Trois groupes V11 (deux au torse, un au crâne ; couleurs de bord Medium_Nougat / Dark_Brown) ne figurent plus en V12 : ces couleurs ne sont plus dans la palette. Quatre groupes (museau, deux pieds, torse) sont inchangés (même position).
Liaisons perdues : pas de tenon supprimé ; les 3 groupes ci-dessus avaient **déjà** 1 à 3 tenons de lien avec le reste. Ce qui est nouveau est que le contour de couleur de la patte (Dark_Tan sur Dark_Orange) laissait une feuille de 69 pièces tenue par 3 tenons, hors de portée d'un renfort plafonné à 60 pièces.

## 3. Correction (générique, sans changer un seuil du validateur)
1. `reinforce.py` : le plafond de taille de groupe devient un paramètre par passe (`max_group_parts`, 60 par défaut pour les configurations historiques, 400 pour V12.1). Le renfort ne recolore que des cellules **cachées** (six voisins occupés) ou re-tuile des plaques de la même couleur : **aucune cellule exposée ne change de couleur** (mesure : 0 cellule exposée différente et 0 cellule d'occupation différente entre l'entrée et la sortie du renfort, Beagle ; 243 cellules cachées recolorées).
2. Pont raccourci (`shorten_on_cut`) : si l'ensemble des cellules de pont coupe un lien entre colonnes, on retente avec moins de cellules et d'autres pavages (sens z, sens x, plaques de 2) avant d'abandonner. Les liaisons existantes ne sont jamais coupées (le contrôle de connectivité global est conservé).
3. Une passe de plus (3 passes, la 3ᵉ ne trouve plus rien : stabilisation).
Reproductibilité des configurations historiques : avec `paco_fixed_v11.json` (palette V11 figée, renfort historique) le Paco V12.1 est **identique octet pour octet à V9.1** (sha256 f878c3b7…) après les modifications ; l'ordre des pièces de sortie du renfort a été préservé à cet effet (un premier essai l'avait modifié, détecté par le hachage, corrigé).
Alternatives écartées : (i) abaisser le seuil des cas (interdit) ; (ii) interdire Orange / Dark_Tan pour Paco : 8 cas et **7 collisions** réapparaissent (le modèle recolore la peau d'oreille) → rejeté ; (iii) coefficient de tenue plus élevé : non touché.
