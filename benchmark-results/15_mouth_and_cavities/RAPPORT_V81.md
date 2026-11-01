# LEGO V8.1 : module automatique de lignes et cavités (bouche de Paco, 400 mm)

Point de départ : commit `7453b2d` (V8). Une seule itération ciblée.

Le GLB source n'est pas modifié. Je n'ai rien acheté ni déployé, et je n'ai rien fusionné dans `main`. Je n'ai pas touché aux mains, aux semelles ni à la notice détaillée des oreilles. Les oreilles et les yeux de V8 sont **inchangés** (§ 5).

## Verdict : **CORRIGER SOUS CONDITION**

**Ce qui marche.** À taille normale, de profil droit, la bouche se lit maintenant comme une ouverture. Le palais et la lèvre forment une ligne sombre, un vide se creuse sous le museau, la mâchoire est visible en dessous, et une langue rouge se voit sur son bord. En V8 il ne restait qu'une barre noire. Vue de dessous et en trois quarts, la bouche est lisible aussi.

**Défaut précis qui subsiste.** La bouche n'est pas lisible de **profil gauche** ni sur la vue de **face**, deux des vues demandées. De ce côté l'ouverture reste fermée par la joue (§ 4). La correction minimale est décrite dans `PROBLEMES_NON_RESOLUS.md`, n° 1.

## 1. Comprendre la bouche réelle (`analyse/`)

Sources : maillage GLB, coupes sagittales (`coupes_sagittales_GLB_et_grille_V8.png`), silhouettes latérales (`silhouette_laterale_GLB_grille_V8.png`), taches de couleur de V8.

| Élément | Ce que contient le GLB | Géométrie |
|---|---|---|
| **Ouverture** | Une encoche entre le museau et la mâchoire, **ouverte vers le bas et vers l'avant**. La lèvre supérieure est le bord inférieur du museau. | Hauteur libre de l'ordre de 9 mm, longueur de l'ordre de 70 mm le long du museau (estimées sur les coupes et la grille fine, sans mesure fine). |
| **Cavité sombre** | Intérieur de l'encoche. Les taches ne sont ni nettes ni sombres : un palais noir de 16,6 × 7,4 mm faisant face vers le bas (`bouche_9`), et une lèvre rouge de 19 × 4,8 mm faisant face vers le bas (`bouche_14`). | Les surfaces sont orientées vers le bas, à 5-7° de la verticale. |
| **Mâchoire** | Un coin court (environ 47 mm) sous l'arrière du museau. | Sa face supérieure est inclinée vers l'avant. |
| **Langue rouge** | Un petit biseau rouge de 12 × 8 mm sur le dessus de la mâchoire (`bouche_15`). | Normale à **30°** de la verticale, vers l'avant et le côté. |
| **Côtés** | La bouche est visible des deux côtés dans le GLB. | Ni la langue, ni la cavité ne sont symétriques. |

**Ce que la grille V8 reproduisait déjà.** L'encoche de 3 à 4 plaques de haut existait bien dans le volume (131 colonnes, 4,6 plaques en moyenne), avec la mâchoire en dessous. La lecture était perdue pour deux raisons :

- l'intérieur était de la même couleur que la peau ;
- la seule tache de couleur ressemblait à une barre noire.

**Éléments constructibles à cette échelle :**

- l'encoche, par la forme du volume : oui ;
- les surfaces tournées vers le bas, par la couleur du dessous et de la tranche des plaques : oui (dessous visible, tranche visible par le côté) ;
- la langue, par une pièce inclinée : oui, une pente fromage rouge, sur un vrai tenon ;
- la profondeur de la cavité : oui, par les parois intérieures sombres.

## 2. Module générique (`generateur/lcm.py`)

Entrées : taches du GLB (`details.json`) et grille de corps après creusement des oreilles et des yeux. Rien n'est propre à Paco : coordonnées et pièces viennent du GLB, de la géométrie LDraw mesurée et de la disponibilité Rebrickable (au moins 20 sets par couleur).

| Traitement | Déclencheur | Ce qu'il fait |
|---|---|---|
| **T1, surface inclinée** | tache faisant face vers le haut | Mesure l'inclinaison de la face supérieure de chaque pièce candidate (tuiles, pentes fromage, pentes 45°) sur son maillage. Choisit pièce, quart de tour et position qui minimisent : écart d'inclinaison + écart de direction + écart d'empreinte (IoU) + saillie. La pièce s'enfiche sur une rangée de tenons réels ; les tuiles dessous deviennent des plaques. |
| **T2, plafond** | tache faisant face vers le bas | Les cellules de surface sous l'empreinte de la tache, et la plaque derrière, prennent sa couleur. |
| **T3, cavité ouverte** | cavité qui contient une tache de bouche | Détection par plafond et plancher (voir ci-dessous). |

**T3, détail.** Sont retenues les cellules vides **ouvertes sur l'extérieur** (remplissage depuis le bord de la grille : les vides laissés par les oreilles ne comptent pas), avec un plafond à au plus 5 plaques au-dessus et un plancher à au plus 6 plaques en dessous. La composante qui touche une tache de bouche est gardée (131 colonnes). Puis :

1. **Hauteur libre** : si elle est inférieure à 3 plaques (9,6 mm), le plafond est creusé jusqu'à 3. Le relief vient de la géométrie, pas de la couleur.
2. **Ligne de lèvre** : le plafond (2 plaques) des colonnes du bord ouvert prend la couleur dominante des taches de plafond.
3. **Langue** : les 2 plaques du plancher proches d'une tache orientée vers le haut prennent sa couleur.
4. **Parois** : les cellules qui bordent la cavité (ce qu'on voit à travers l'ouverture) prennent la couleur de l'intérieur.

**Variantes comparées**

- **A, relief réduit** : T1 et T2 seuls, sans cavité.
- **B, cavité ouverte** : A plus T3 (retenue).

Les trois pièces candidates qui reviennent sont des plaques, des tuiles et une pente fromage. Aucune pièce n'a été imposée à la main.

**Capacités génériques et limites** : voir `CAPACITES_GENERIQUES.md`.

## 3. Résultat sur la sculpture (`modeles/`)

Pièces utilisées :

| Élément | Quantité |
|---|---|
| Pente fromage rouge 1×1 (54200) | 1 |
| Plaques de revêtement | 223 cellules recolorées (+ 22 creusées) |

**Langue.** Pente fromage 31° sur un tenon réel. Écart d'inclinaison avec la tache : 0,4°. **Écart de direction : 28,5°** (le choix se fait par quart de tour). IoU de l'empreinte 1,0, saillie 0,9 plaque.

| Zone | V8 | V8.1 (B) |
|---|---|---|
| Colonnes sous 3 plaques de hauteur libre | 34 | **15** (celles qui touchent des cellules protégées ou le plancher sans marge) |
| Hauteur libre moyenne (plaques) | 4,59 | 4,75 |
| Cellules sombres visibles (zone et voisines) | 10 | **70** |
| Cellules rouges visibles | 8 | **21** |

Ces mesures complètent l'évaluation visuelle sans la remplacer.

## 4. Évaluation visuelle (`comparaisons/`)

Vraies pièces LDraw, mêmes vues et même lumière. Critère prioritaire : lisibilité **à taille normale, sans zoom**.

| Vue (taille normale) | V8 | V8.1 B | Constat |
|---|---|---|---|
| **Profil droit** | barre noire épaisse + moignon | ligne sombre fine au bord du museau, vide net, mâchoire en dessous, langue rouge visible, intérieur sombre | **La bouche se lit comme une bouche ouverte.** Net progrès. |
| **Dessous du museau** | quelques cellules rouges et sombres | langue rouge et plafond sombre lisibles | Lisible. |
| **Trois quarts (droit, bas)** | tache rouge ponctuelle | langue rouge et cavité sombre | Lisible. |
| **Gros plan de la bouche, droite** | idem profil droit | idem profil droit | Bon. |
| **Profil gauche** | rien | quelques cellules sombres près de la mâchoire, pas de langue | **Non lisible.** Défaut restant. |
| **Face** | rien | rien | Non lisible (le GLB aussi montre peu de bouche de face). |
| Proportions du museau, truffe, yeux, oreilles | — | inchangés | Aucune dégradation (§ 5). |

**Pourquoi le profil gauche reste muet : cause non établie avec certitude.** Ce que j'ai vérifié : sur les lignes de vue horizontales de la caméra gauche, le GLB n'est **pas** transparent dans l'encoche (le coin de la mâchoire et la joue bloquent le regard comme dans la grille). Le vide qu'on y voit sur le GLB n'est donc pas un trou traversant. Le GLB y montre un intérieur clair avec un fin liseré rouge, que la grille reproduit mal parce que le liseré mesure moins d'une cellule. Mon hypothèse est que les revêtements (ligne de lèvre, langue, parois) se trouvent surtout du côté de la grille que regarde la caméra droite, à cause de la diagonale du museau (32° par rapport aux axes de la grille). Je n'ai pas testé de percement de la joue : cela changerait la forme du museau sans preuve que le GLB l'exige.

**Défaut visuel ajouté :** la ligne de lèvre laisse quelques traits sombres isolés sur le bas du museau (cellules du bord ouvert de la cavité).

**Variante A (relief réduit)** : presque pas de différence avec V8 (14 cellules sombres visibles, 10 rouges). Une pièce incrustée et un revêtement par taches **ne suffisent pas**. Le relief demande l'ouverture de la cavité (B).

## 5. Contrôles techniques (`validation/`)

| Contrôle | V8 | V8.1 B |
|---|---|---|
| Pièces / types | 2 758 / 41 | **2 796 / 42** |
| Collisions (`validate_v3`) | 0 | **0** |
| Déconnectées / îlots / non soutenues / tenons bouchés | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** |
| Étapes de la notice | 331 | **335**, aucune pièce non ordonnée |
| Couples pièce × couleur | 72, tous vérifiés | **74, tous vérifiés** (nouveau : 54200 rouge) |
| Sous-ensembles sous 0,5 N | 49 | **43** |
| Force minimale | 0,07 N | 0,07 N |

**Non-régression :**

- **Oreilles V6.1 de la sculpture** : 337 pièces identiques à V8 (positions et matrices), appuis 4+2 et 7+5.
- **Yeux et truffe** : mêmes 8 pièces, mêmes positions.
- **V6 et V6.1 rejoués** à partir des entrées archivées, après toutes les modifications de V7, V8 et V8.1 : **aucune différence** (modèles, rapports, validations, nomenclatures). Voir `non_regression/`. Les références historiques n'ont pas été modifiées.
- **Chaîne V8** : la chaîne par défaut (sans le drapeau V8.1) redonne exactement `paco_V8.ldr`. Seul changement dans `microdetails.py` : un drapeau d'environnement `MD_SKIP_MOUTH`.

**Montage de la bouche** (`comparaisons/montage_bouche_*`). Les couches 78 à 92, vues en 3/4 puis de profil, montrent l'ordre de pose : mâchoire et langue, puis plafond et ligne de lèvre. Tout se monte par le dessus et les côtés, sans pièce accrochée sous le museau. La pente rouge se pose sur un tenon, après remplacement de la tuile dessous par une plaque.

## 6. Nouveaux points faibles : voir `NOUVEAUX_POINTS_FAIBLES.md`

## 7. Décision

CORRIGER SOUS CONDITION. Le défaut précis et limité est la lisibilité de la bouche de profil gauche et de face (`PROBLEMES_NON_RESOLUS.md`, n° 1), dont la cause reste à établir. La méthode ne nécessite aucune conception propre à Paco.
