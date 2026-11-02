# Limites physiques et risques : Beagle V10 et moteur 1

**Aucun essai physique, aucun achat.** Tout ce qui suit est calculé ou supposé.

| # | Risque | Gravité | Base |
|---|---|---|---|
| 1 | **Plan d'appui du Beagle** : 18 pièces touchent le plan le plus bas, en 10 plaques de 0,6 à 3,2 cm² (17 cm² au total) ; l'enveloppe convexe (487 cm², marge de 78,8 mm) ne dit pas que la statue repose sur une surface plane. Balancement possible ; pression locale sur la table | **Élevée** | `validation/stabilite.json` ; même défaut que Paco en V7 à V9 |
| 2 | **Masse réelle inconnue** : 5 253 g est la masse du **modèle** (0,10 g par case, calibré sur des briques) ; la sculpture, de plaques, est plus lourde. Les pattes (17 cm² de contact) portent plusieurs kilos | Élevée | Aucune pesée |
| 3 | **Approvisionnement** : 919 plaques 4×6 (3032) en Dark Orange, une référence présente dans 21 sets ; 77 couples « vérifiés » dans Rebrickable, mais les **quantités** ne sont pas vérifiées | Moyenne | `nomenclature_complete.csv` |
| 4 | **Oreilles pendantes sans fixation dédiée** : plaques du volume tenues par des tenons verticaux ; non modélisées comme un module | Moyenne | Aucun cas d'oreille identifié séparément dans les 7 groupes fragiles, mais non vérifié |
| 5 | **7 groupes fragiles** de 1,0 à 1,9 g, 0,10 à 0,47 N (1 N par tenon, traction et moment, sans cisaillement ni frottement) | Moyenne | `validation/weak_final.json` |
| 6 | **2 pièces à tenir** et 1 333 poses par le dessous (marge du centre de gravité ≥ 71 mm) | Faible | `validation/suspendues.json` |
| 7 | **Notice non suivie** : 581 étapes de 20 pièces, linéaires ; accessibilité des doigts, forces d'emboîtement, tolérances non modélisées | Moyenne | Contrôles numériques seulement |
| 8 | **Couleurs réelles** : écart d'environ 100 sur 255 avec le GLB ; teintes Dark Orange / Medium Nougat jugées sur écran, pas sur pièces | Moyenne | `validation/fidelite_silhouette.json` |
| 9 | **Modèle de résistance** : 1 N par tenon supposé, rigide, sans cisaillement, torsion, fatigue | Élevée (pour toute conclusion) | `validate_v3.py` inchangé |
