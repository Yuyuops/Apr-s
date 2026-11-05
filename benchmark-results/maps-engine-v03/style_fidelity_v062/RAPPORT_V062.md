# LEGO Maps V0.6.2 — flancs courbes et finition (test local)

Branche `research/lego-maps-v062-organic-relief`. Moteur 1 non modifié, aucun achat, aucune fusion dans `main`.
Tous les rendus viennent de vrais maillages LDraw. Aucune validation physique n'a été faite (`physical_test: false`).

## 1. Protocole
- Trois zones locales de 40×40 tenons, avec la même échelle (tenons par degré) que le prototype 64×96, la même palette C2, la même caméra et le même éclairage.
- Quatre variantes par zone :
  - `vertical` : flancs verticaux de V0.6.1 ;
  - `curved` : pentes courbes, cycle 1 ;
  - `curved2` : pentes courbes, cycle 2 ;
  - `plates` : transitions progressives en plaques et tuiles.
- Pièces utilisées : 11477 (1×2) et 15068 (2×2). La géométrie, l'orientation, l'appui sur tenons, les collisions et la disponibilité de chaque couple pièce/couleur sont vérifiés (voir `VERIFICATION_PIECES_COURBES.md`).
- Aucune substitution de couleur : 0 substitution sur les 12 variantes.

## 2. Résultats mesurés (12/12 variantes, moteur 1 en lecture seule : 0 collision, 0 pièce déconnectée, 0 îlot, 0 non supporté)
| zone | vertical | pentes c1 | pentes c2 | plaques |
|---|---|---|---|---|
| Sicile (côte) | 3606 | 3865 | 3963 (+357, +9,9 %) | 4032 (+426) |
| Golfe (plusieurs strates) | 4020 | 4171 | 4276 (+256, +6,4 %) | 4382 (+362) |
| Littoral adriatique (coins concaves et convexes) | 4000 | 4079 | 4144 (+144, +3,6 %) | 4202 (+202) |

Références distinctes : 90–91 en vertical, 96–98 en pentes c2.
Couverture des parois par une pente courbe, cycle 2 : Sicile 291/505 (58 %), Golfe 268/473 (57 %), Littoral 155/293 (53 %).

## 3. Jugement visuel (honnête)
Comparatifs : `comparatifs/flancs_*` (cycle 1) et `comparatifs/flancs2_*` (cycle 2, V0.6.1 / c1 / c2).
- **Vue oblique ou rapprochée, cycle 2** : le gain est réel mais modéré. Les marches verticales en briques laissent place à des flancs arrondis qui suivent les strates (golfe, Sicile). La côte se lit comme un talus plutôt que comme un escalier.
- **Vue de face** (celle du tableau fini) : le gain est quasi invisible. Le dessin des strates ne change pas.
- **Cycle 1** : plaques et pentes isolées en « doigts », sans gain net.
- **Plaques progressives** : le gain visuel est moindre que celui des pentes, pour un coût plus élevé (+362 à +426 pièces). Piste écartée.
- **Cohérence** : la couverture reste de 53–58 %. Le reste des parois est vertical, d'où un mélange de deux grammaires qui paraît irrégulier.

## 4. Coins concaves et bloqueur
- Une côte en escalier sur grille produit surtout des cellules de paroi concaves ou à deux parois.
- Aucune pièce à profil de coin intérieur n'est vérifiée (93273 n'est pas au catalogue). Le moteur oriente donc une pente sur une seule paroi. Le coin reste un angle vif, ce qui est visible dans la zone littoral.
- Une pente arrondie n'est pas présentée comme résolvant le coin concave : son profil ne correspond pas à ce cas.
- Deux approches de pentes courbes ont été essayées (c1, c2) et une approche par plaques. Bloqueur documenté : absence de pièce de coin concave vérifiée, et couverture limitée par la géométrie en escalier de la côte.

## 5. Cadre : blanc actuel vs blanc plus travaillé avec sous-ensembles dorés
Test sur la zone golfe, flancs courbes, cadre 4 tenons (`comparatifs/cadre_A_vs_B.png`).
- Le cadre B (`italia_prestige_frameB`, ornement `scroll` 7×7 en pièces dorées réelles) valide 0/0/0/0.
- **Échec** : l'ornement n'est pas posé sur le cadre. Il apparaît en patchs de tenons dorés dans les trois coins intérieurs de la carte, par-dessus la mer. Il dégrade l'image et n'apporte rien au cadre, qui reste identique à A (blanc, coins dorés).
- Pas de fausses volutes ni de pièce personnalisée. L'ornement est rejeté tel quel. Une version correcte demande de placer l'ornement sur la bande du cadre. Ce travail n'est pas fait.

## 6. Décision sur le prototype complet
Le gain démontré sur les zones ne justifie pas de régénérer l'Italia Prestige 64×96.
- Pas de notation à 20/25 : la note reste 15/25 (V0.6.1), sans critère artificiellement relevé.
- Pas de lancement de l'Italie 128×192 ni d'Atlas Natural.
- Module figurines : inchangé, désactivé par défaut. Intégration 3D non validée.

## 7. Suite proposée
1. Vérifier et ajouter au catalogue une pièce de coin concave réelle (par exemple 93273) avec orientation et connexions.
2. Pousser la couverture des parois à 80 % ou plus et traiter les parois à deux faces, avant tout test de prototype complet.
3. Refaire le test d'ornement avec une pose sur la bande du cadre.

Les sorties légères sont dans `results/<zone>_<variante>/` : LDraw, `parts.json`, `metrics.json`, `independent_validation.json`, `parts_list.csv`, rendus face, oblique et zoom.
Les dossiers `work/` (maillages de rendu, environ 1,9 Go) ne sont pas versionnés.
