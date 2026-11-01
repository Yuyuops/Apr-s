# Décision : LEGO V5.1

## Verdict : **CHANGER LA FIXATION**

**La forme est réussie. La fixation n'atteint pas le niveau demandé.**

| Exigence | Résultat V5.1 |
|---|---|
| Amélioration visible de face | **Oui.** L'oreille a le volume de la référence (20,8 mm contre ≈ 20 mm) et n'a plus de pied. |
| Amélioration visible au raccord | **Oui.** Plus de pied, plus de plaque apparente, plus de jour : le lobe entre dans le crâne. Restent quelques taches noires au pied de la racine. |
| Gains conservés sur les 4 autres vues | **Oui.** La face intérieure est même meilleure : tuilée au lieu de fonds de pièces. |
| Silhouette | Meilleure que V5 (0,943 / 0,942 contre 0,923 / 0,939), encore sous C (0,955 / 0,958) |
| 0 collision, 0 pièce déconnectée, notice réalisable | **Oui** (0 / 0 / 0 pièce posée sans liaison, 85 étapes) |
| Pièces et couleurs vérifiées | **Oui** (29 couples, au moins 27 sets) |
| Rendus réels, sans IA | **Oui** |
| Poids | **2,3 fois plus lourd** que V5 (86,8 g contre 37 g). C'est la conséquence directe de l'épaisseur, malgré l'âme ajourée. |
| Résistance, avec plusieurs chemins de connexion indépendants | **Non atteint.** La force au bout double (0,16 → 0,32 N) et 5 vrais tenons remplacent 2 pivots. Mais il n'y a **qu'un seul chemin** (une plaque noyée), et le coefficient sous le poids propre **baisse** (3,47 → 2,17). Une oreille de 87 g qui se décroche sous 0,32 N au bout n'est pas assez robuste pour un modèle manipulé. |

Les deux premières réserves (épaisseur, raccord) sont levées. La troisième (tenue) n'est que partiellement levée : d'où le verdict.

## Pistes pour la fixation (non engagées, à décider)

1. **2e chemin indépendant :** une 2e plaque tournée à un autre niveau, sous le bord inférieur du lobe, au contact du crâne, avec ses propres coïncidences.
2. **Plus de coïncidences** sur une plus grande plaque noyée (6×8, 8×8) si le volume de la tête le permet. On en compte 7 à 8 dans la recherche faite ici, mais la plaque affleure.
3. **Alléger** : âme plus ajourée, ou épaisseur variable plus marquée (bord à 24 LDU, centre à 52 LDU).
4. **Essai physique** de la liaison seule, sur une maquette réduite : plaque tournée + 5 tenons, avant tout autre calcul.

V5 reste intacte dans `09_designed_ear_proof/`. **Aucun autre développement n'est commencé avant votre décision.** Rien n'est fait sur le moteur de tableaux 3D.
