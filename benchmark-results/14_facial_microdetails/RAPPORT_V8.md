# LEGO V8 : micro-détails du visage (Paco cartoon, 400 mm)

Point de départ : commit `9774bdb` (V7). La chaîne V7 est reprise sans changement de fond. On y ajoute un détecteur et un générateur de micro-détails.

Le GLB de référence n'est pas modifié. Aucun achat, aucun déploiement, aucune fusion dans `main`. Les mains, la notice détaillée et le moteur 2 n'ont pas été touchés.

## Verdict : **CORRIGER**

**Ce qui marche.** Les yeux et les pupilles sont produits automatiquement avec de vraies pièces, et le regard est nettement plus fidèle. La truffe est une vraie coupole noire. Les contrôles passent :

- 0 collision, 0 pièce déconnectée ;
- oreilles V6.1 identiques à V7 ;
- non-régression V6 / V6.1 sans aucune différence.

**Le défaut qui empêche la validation : la bouche.** Elle n'est pas plus lisible qu'en V7. Le palais regarde vers le bas, et aucune pièce à tenons ne peut se fixer dans cette direction. La langue n'est rendue que par une tuile 1×1 rouge, presque invisible. Détails au § 6.

## 1. Analyse de la géométrie (`generateur/detect.py`, `analyse/details_detectes.json`)

Méthode, sans aucune coordonnée propre à Paco :

1. Les faces du maillage de la tête sont classées par couleur (blanc, noir, rouge, peau). On forme des taches connexes, puis on fusionne celles d'une même couleur qui sont à moins de 6 mm.
2. Les taches posées sur une zone « oreille » de la segmentation V7 sont ignorées.
3. Pour chaque tache, on mesure :
   - l'aire, le centre et les dimensions dans son plan ;
   - le diamètre équivalent et le bombé ;
   - le taux de remplissage d'un disque ;
   - la **normale extérieure**, dont le signe est vérifié sur la grille fine : le GLB miroir a ses faces inversées.
4. Repère de la tête : axe du museau (centre du crâne vers centre du museau), plan sagittal ajusté par symétrie miroir du maillage (écart médian 3,0 mm).
5. Classes :
   - **œil** : tache claire qui contient une tache sombre (la **pupille**) ;
   - **truffe** : tache sombre la plus avancée sur le museau, plus les taches sombres voisines ;
   - **bouche** : tache rouge ou sombre, tournée vers le haut ou le bas, sous les yeux ;
   - **marque** : tout le reste (sourcils, traits, taches), laissé aux couleurs du volume.

**Ce que le GLB contient réellement**

| Détail | Centre (mm) | Taille | Normale extérieure | Remarque |
|---|---|---|---|---|
| Œil droit (`oeil_2`) | 177 / 311 / −146 | 23,9 × 20,9 mm, pupille 8,1 mm | latérale, 15° de l'axe +X | disque complet (remplissage 1,03) |
| Œil gauche (`oeil_1`) | 123 / 308 / −149 | 23,3 × 19,4 mm, pupille 8,0 mm | latérale, 22° de −X | disque complet (1,11) |
| **Troisième œil** (`oeil_douteux_0`) | 146 / 323 / −176 | 24,0 × 19,4 mm, pupille 8,8 mm | avant-gauche | disque incomplet (0,61). **Artefact du GLB** : deux yeux sur le côté gauche. |
| Truffe | bout du museau | 2 taches noires à 25 mm l'une de l'autre, de part et d'autre du bout | bout du museau, **37°** de l'axe +Z | enveloppe le bout |
| Bouche | sous le museau | palais noir 16,6 × 7,4 mm (vers le bas), langue rouge 12 × 8 mm (vers le haut), bord rouge 19 × 4,8 mm (vers le bas) | ±Y | ouverture d'environ 1 couche dans le volume |
| Marques | sourcils derrière les yeux, trait sur le museau, petit trait de joue, racine noire des oreilles | — | — | non traitées (hors mission), couleurs V7 |

**Les détails ne sont pas tous ronds :**

- la truffe enveloppe le bout du museau ;
- la bouche est une cavité, avec des surfaces tournées vers le haut et vers le bas ;
- les marques sont des traits.

## 2. Générateur (`generateur/microdetails.py`, `analyse/microdetails_decisions.json`)

**Catalogue générique.** Il regroupe des familles de pièces de surface réelles :

- tuiles et plaques rondes 1×1 et 2×2 ;
- coupoles (dish) 2×2, 3×3 et 4×4 ;
- tuiles 1×1 à 1×4 et tuile 1×1 à bout arrondi ;
- brique 1×1 à tenon latéral (SNOT) ;
- plaque ronde 1×1 comme cale.

Chaque propriété utilisée est **mesurée sur la géométrie LDraw** : diamètre, bombé, tenon central sur le dessus, points de réception. Une pièce n'est retenue dans une couleur que si Rebrickable la recense dans au moins 20 sets.

**Choix de forme et de taille (pièces rondes).** On prend la pièce qui minimise un coût :

- erreur de diamètre ;
- + 0,5 × erreur de bombé ;
- + 1 si une pupille est nécessaire et que la pièce n'a pas de tenon central ;
- + 0,2 si un tenon resterait visible.

La pupille est la pièce ronde la mieux adaptée, posée sur le tenon central.

**Direction de fixation.** C'est l'axe de la grille le plus proche de la normale extérieure. L'angle entre les deux donne la confiance : haute en dessous de 20°, moyenne en dessous de 35°, faible au-delà.

**Pose latérale :**

- une brique SNOT est placée dans le volume, avec des cellules du corps au-dessus et en dessous ;
- on ajoute 0 à 2 cales ;
- on choisit le point de réception de la pièce ;
- coût = écart entre le centre de la pièce et le centre du détail du GLB + 0,5 × écart entre la face extérieure et la surface du GLB (+ bombé).

La pièce est donc **encastrée à la surface du GLB**, et non collée sur le volume.

**Pose sur une surface tournée vers le haut.** Une tuile est incrustée dans la couche supérieure. Sa forme est celle qui recouvre le mieux l'ellipse de la tache (IoU maximal).

**Surface tournée vers le bas.** Aucune pièce à tenons ne peut s'y fixer. Seule la couleur du volume est appliquée, et le cas est signalé comme capacité manquante.

**Espace :**

- on creuse les cellules touchées par les nouvelles pièces (dilatées dans le plan, jamais vers l'arrière) ;
- on creuse aussi la ligne de vue, selon l'axe de pose **et** selon la vraie normale du GLB ;
- sont **réservées** : les pièces des oreilles et les cellules qui portent les appuis de leurs fixations ;
- une position qui toucherait une cellule réservée, un autre détail ou les cellules qui tiennent la brique SNOT est rejetée.

**Couleurs.** Autour d'un détail construit, les cellules voxel de sa couleur prennent la couleur de la peau. Exception : une truffe qui enveloppe le bout garde ses flancs noirs.

**Œil douteux.** Les yeux sont appariés par symétrie miroir. Le score combine :

- la distance au miroir ;
- l'écart d'aire ;
- l'écart de normale ;
- le remplissage du disque.

Pour le côté gauche, le candidat retenu (`oeil_1`) a un score de 30,5, contre 37,6 pour l'autre. L'œil restant n'est pas construit et ses cellules blanches sont recolorées.

## 3. Résultat de l'intégration

| Détail | Pièces choisies | Pose | Écart du centre | Face extérieure par rapport au GLB | Inclinaison / confiance |
|---|---|---|---|---|---|
| Œil droit | coupole 3×3 blanche 43898 (24 mm, cible 22,3 mm) + tuile ronde 1×1 noire 98138 (8 mm, cible 8,1 mm) | SNOT 87087, +X, 0 cale | 1,8 mm | +0,1 mm | 15° / haute |
| Œil gauche | idem | SNOT 87087, −X | **7,6 mm** (67 positions rejetées près de la racine de l'oreille haute) | **+4,3 mm** | 22° / moyenne |
| Truffe | coupole 3×3 noire 43898 (24 mm, cible 24,7 mm) | SNOT 87087, +Z | 1,4 mm | +2,2 mm (bombé du GLB environ 3 mm) | **37° / faible** |
| Langue | tuile 1×1 rouge 3070b incrustée (IoU de forme 0,74) | sur le volume | — | affleurante | 30° / moyenne |
| Palais, bord de lèvre | couleur du volume (4 + 6 cellules) | — | — | — | capacité manquante |

**Rapport pupille / œil :** 0,33 en LEGO, contre 0,36 dans le GLB (yeux droit et gauche).

**Bilan chiffré :**

- 9 pièces de détail ;
- 144 cellules creusées pour les détails (1 197 pour les oreilles, inchangé) ;
- 36 cellules recolorées.

## 4. Évaluation visuelle

Fichiers : `comparaison_GLB_V7_V8.png`, `gros_plans_visage_GLB_V7_V8.png`, `visage_grand_format.png`. Vraies pièces LDraw, mêmes vues et même lumière.

| Critère | V7 | V8 | Constat |
|---|---|---|---|
| Position des yeux | Taches blanches et noires en escalier, mal situées | Disques blancs à pupille centrée, un par côté | **Nettement mieux.** L'œil droit est bien placé. L'œil gauche est un peu plus bas et en arrière que dans le GLB (7,6 mm). |
| Expression du regard | Illisible | Regard rond, « cartoon », comme le GLB | **Nettement mieux.** Les pupilles sont centrées, comme dans le GLB. |
| Forme de la truffe | Grand bloc noir rectangulaire sur le flanc du museau | Coupole noire au bout du museau | **Mieux de trois quarts.** De profil, la coupole se voit peu, car elle regarde à 37° de la vraie direction du bout. |
| Lisibilité de la bouche | Trait sombre sous le museau, visible de profil droit | Pareil, avec une tuile rouge à peine visible | **Pas d'amélioration.** Toujours peu lisible de profil gauche. |
| Raccords au museau | — | Coupoles encastrées, sans socle visible ; taches blanches éliminées | Bons. Un peu de jaune en retrait autour des coupoles (logement carré pour une pièce ronde). |
| Reconnaissance générale | Bonne | Meilleure | Le visage « regarde » enfin. Silhouette et oreilles inchangées. |

**Défauts hérités de V7, non traités :** les traits noirs parasites sur le museau et les sourcils voxelisés (classe « marque »), le logo de la salopette, les mains.

## 5. Contrôles techniques (`validation/`)

| Contrôle | V7 | V8 |
|---|---|---|
| Pièces / types | 2 773 / 43 | **2 758 / 41** |
| Collisions (`validate_v3`, géométrie réelle) | 0 | **0** |
| Pièces déconnectées / îlots / posées dans le vide / tenons bouchés | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** |
| Étapes de montage | 331 | **331**, toutes réalisables |
| Couples pièce × couleur | 68, tous vérifiés | **72, tous vérifiés** (Rebrickable) |
| Nouvelles références | — | 87087 jaune × 3, 43898 blanc × 2, 43898 noir × 1, 98138 noir × 2 (plus 3069b rouge × 2 venant du volume) |
| Oreilles | — | **337 pièces identiques à V7.** Mêmes plaques tournées, appuis 4+2 / 7+5. |
| Sous-ensembles sous 0,5 N | 46 | **49** |
| Force minimale | 0,07 N | 0,07 N |

**Fixation des nouveaux détails :**

- chaque brique SNOT est tenue en haut et en bas par le corps ;
- chaque coupole tient sur **1 tenon** latéral, chaque pupille sur 1 tenon ;
- la masse est de l'ordre de 1 g, donc la tenue sous le poids propre n'est pas un problème ;
- en revanche, un tenon unique s'arrache à la main (environ 1 N supposé). Les pièces sont protégées par leur logement.

**Nouveaux points faibles, créés par la reconstruction du volume :**

- un groupe de 10 pièces noires et rouges derrière l'œil gauche, tenu par 1 tenon (0,07 N) ;
- un reste de 7 pièces jaunes du bout du museau, devant la truffe, tenu par 2 tenons (0,19 N).

Les problèmes connus des mains et des bords sont **toujours présents** : main rouge (0,07 N), petits groupes de bord d'oreille, semelles tenues par 5 tenons.

## 6. Non-régression V6 / V6.1 (`non_regression/`)

On a rejoué V6 (`autogen.py`, modifié en V7) et V6.1 (`autogen61.py`) sur les entrées archivées. L'empreinte md5 des silhouettes est identique aux archives. Les commandes sont celles des `run_all.sh` archivés. Les sorties vont dans un dossier séparé ; **les références n'ont pas été modifiées**.

| Cas | Modèles LDraw | Rapport du générateur | Validations | Nomenclature |
|---|---|---|---|---|
| V6 A Paco | oreille 162 et tête + oreille 1 313 pièces : identiques ligne à ligne | 0 différence | v2 : 0 différence | identique |
| V6 B Beagle | 247 pièces : identiques | 0 | v2 : 0 | identique |
| V6.1 A Paco | 170 et 1 321 pièces : identiques | 0 | v3 : 0, v2 : 0 | identique |
| V6.1 B Beagle | 276 pièces, notice comprise : identiques | 0 | v3 : 0, v2 : 0 | identique |

**Verdict : aucune différence.** Les modifications de V7 n'ont pas changé le comportement de V6 ni de V6.1.

## 7. Capacités automatiques et limites

**Automatique et générique :**

- détection des taches de couleur, normale, taille, bombé, appariement des yeux ;
- choix de pièce mesuré sur la géométrie LDraw et la disponibilité réelle ;
- pose SNOT encastrée, réservation des oreilles, ligne de vue, nettoyage des couleurs.

**Règles réglées au vu de ce cas (à confirmer sur un autre personnage) :**

- **Remplissage du disque dans l'appariement des yeux.** Sans ce terme, l'artefact `oeil_douteux_0` aurait été choisi (score 28,5 contre 30).
- **Distance de regroupement de la truffe :** 0,35 × longueur du museau.
- **Diamètre d'une tache qui enveloppe un bout :** pris sur sa largeur.

**Non traité, et signalé comme tel :**

- surfaces tournées vers le bas ;
- traits (sourcils, ligne de bouche) ;
- détails inclinés à plus de 35° d'un axe de la grille, faute de pièce orientable.
