# Notice V9.1 : oreilles, pièces posées par le bas, étapes non confirmées (phases 4 et 5)

Fichiers : `notice/paco_V91_*.pdf` (5 PDF, 203 pages, 12,6 Mo), `modeles/paco_V91_notice.ldr` (LDraw ordonné), `notice/plan_notice.json` (plan complet avec les contrôles de chaque étape), `notice/etapes_notice.csv`, `notice/arbre_notice.json`, `notice/plans_oreilles.json` (séquence, orientation et contrôles de chaque pièce d'oreille), `validation/suspendues_v91.json`.

## 1. Contenu

3 098 pièces, **201 étapes**, 0 pièce absente du plan, **0 étape en défaut** au rejeu des contrôles. Les 5 PDF : corps étapes 1 à 62 (avec couverture et page de précautions), corps étapes 63 à fin, bras et mains, détails du visage, oreilles. Chaque étape : vue de la construction (déjà posé en pâle, pièces à poser en couleur), liste des pièces par référence, nombre et sens des emboîtements, remarques (en rouge : à tenir à la main, emboîtement par le dessous).

Aucune étape ne cache plusieurs dizaines de pièces sans construction préalable : le corps avance par **au plus 20 pièces**, les oreilles par **au plus 8 pièces**, les bras par 20. L'attache d'une oreille (≈ 190 pièces) ou d'un bras (123 à 138 pièces) vient **après** ses 22 à 24 (oreille) ou 6 à 7 (bras) étapes de construction, et ne montre qu'un sous-ensemble déjà fini. Les deux unités de l'oreille basse (2 pièces chacune) ont leur propre étape de construction puis d'assemblage.

## 2. Les oreilles, pièce par pièce

Séquence : `generateur/seq.py` (voir `RAPPORT_31_PIECES.md`), orientation et stabilité : `generateur/ear_plan.py`.

**Orientation sur la table.** Trois orientations sont essayées (debout, à plat face externe vers le haut, à plat face interne vers le haut). Pour chacune, chaque état partiel est jugé : son centre de gravité doit tomber dans l'enveloppe convexe de l'empreinte des pièces les plus basses ; chaque emboîtement est classé par le dessus, de côté ou par le dessous par rapport à la table. Choix : le moins d'états instables, puis le moins d'emboîtements par le dessous.

| Oreille | Orientation retenue | Étapes | Par le dessus | De côté | Par le dessous | Étapes instables |
|---|---|---:|---:|---:|---:|---:|
| Haute | **debout** | 176 | 57 | 106 | 12 | **0** |
| Basse | **à plat, face extérieure contre la table** | 186 | 58 | 70 | 57 | **8** |
| Haute, attache 2 (5 pièces) | à plat | 5 | 4 | 0 | 0 | 0 |

* Les emboîtements « de côté » sont les faces SNOT (plaques et tuiles poussées selon la normale de l'oreille contre le noyau).
* **L'oreille basse ne peut pas rester debout** (174 états instables sur 186 : sa base est une seule brique 1×1). À plat, 57 pièces sont poussées par le dessous : **il faut tenir l'oreille en l'air ou la retourner** pour ces étapes (signalé en rouge). Les 8 premières étapes demandent de maintenir l'assemblage.
* Chaque page d'étape d'oreille montre une **vue éclatée** : les pièces à poser sont décalées de 140 ldu (56 mm) dans la direction d'où elles arrivent ; l'orientation de l'oreille est écrite sous le titre.
* Les pièces à emboîter dans des directions différentes dans la même étape sont comptées (« 3 vers le haut, 5 dans la direction (−0,8 ; 0 ; 0,6) »).

**Vérification** : 0 défaut au rejeu indépendant (géométrie différente, pas de 1 ldu) pour les 181 + 186 pièces d'oreille de Paco V9.1, les 170 de l'oreille V6.1 isolée de Paco et les 276 du Beagle (`validation/replay_*.json`). Voir `RAPPORT_31_PIECES.md` § 4.

## 3. Les 338 pièces à emboîter par le dessous (hors oreilles)

`generateur/suspended_analysis.py`, `validation/suspendues_v91.json`. Ce sont les pièces qui n'ont rien sous elles au moment de la pose (surplombs) : elles sont poussées vers le haut contre la pièce qui les tient, après elle.

| Module | Pièces | Zones | Modèle tenu ? |
|---|---:|---|---|
| Corps (ligne principale) | **283** | (voir ci-dessous) | **non** |
| Bras gauche | 20 | torse, jambes | **oui, à tenir** |
| Bras droit | 35 | torse, jambes | **oui, à tenir** |

Répartition des 338 par zone du personnage : pieds 35, jambes 113, torse 80, crâne 20, museau 89, autre 1.

* **Corps** : pour chacune des 283 pièces, le modèle déjà posé (jusqu'à 1 105 g) est **stable sur son plan d'appui** : le centre de gravité est à **au moins 33,9 mm** de l'arête de l'enveloppe d'appui (26 plaques, 132 cm²). La force d'emboîtement supposée (1 N par tenon engagé, vers le haut, à l'endroit de la pièce) donne un coefficient de sécurité de basculement **d'au moins 4,1** (calcul statique, moment du poids contre moment de la poussée autour de chaque arête de l'enveloppe). L'insertion se fait par le dessous du surplomb ; elle est possible dans l'ordre prévu, sans faire tenir un ensemble instable. Le chemin d'accès est libre (contrôle de chemin de V9, inchangé).
* **Bras** : l'avant-bras se construit debout sur la main (colonne étroite, 32 à 34 g). À ces 55 poses, **le centre de gravité sort de l'empreinte** (jusqu'à −21 mm) : le bras en construction **doit être tenu à la main**. Signalé en rouge sur les pages concernées (étapes 73 à 85) et dans la page de précautions. Un montage à plat des bras n'a pas été étudié.

Limites de ce contrôle : pièces rigides, force d'emboîtement supposée égale à 1 N par tenon (non mesurée), aucune mesure de la hauteur libre sous les pièces pour la main, aucune étude de la prise des doigts.

## 4. Ordre du fichier LDraw et pièces posées « en pont »

Le validateur de V9 comptait **18** pièces posées avant toute liaison avec les pièces déjà posées ; V9.1 n'en compte plus que **3** (2 pièces de bras, 1 pièce d'oreille) : ce sont des pièces appuyées sur la table ou sur une pièce voisine, **verrouillées par la pièce suivante** (indiquées « pose sur un appui sans emboîtement » dans la notice). 0 collision, 0 pièce déconnectée, 0 îlot.

## 5. Étapes que les contrôles numériques ne confirment pas

1. **Toutes les étapes sont des possibilités du modèle** : translations rigides, aucun doigt, aucune force réelle, aucune flexion.
2. **Les 55 poses de bras** (tenir le bras) et les **57 poses par le dessous de l'oreille basse** : l'instabilité et l'accès à la main sont jugés par un calcul, pas par un montage.
3. **Les 8 premières étapes de l'oreille basse** à plat : instables au sens du modèle (centre de gravité hors de l'empreinte des premières pièces).
4. **L'engagement réel** de chaque pièce : le dégagement de 5 ldu (2 mm) le long de l'axe garantit que les tenons se libèrent ; la force d'emboîtement et la tolérance des tenons ne sont pas modélisées.
5. **La notice n'a pas été suivie par un monteur** : aucune étape n'a été exécutée.
