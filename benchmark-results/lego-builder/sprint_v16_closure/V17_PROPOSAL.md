# Proposition V17 — trois améliorations prioritaires (non développées)

Principe : gain visuel maximal à pièces ≈ constantes, sans dégrader la solidité mesurée en clôture V16 (liens faibles ≤ 3, C1 ≤ 108, aucune collision). Budget de départ V17 : **≤ +6 % de pièces** (≤ ≈ 11 850) et **C3 (décoratives exposées) ≤ 17 % des pièces**. Rappels : aucune note artistique sans validation humaine ; aucun gel sans accord.

## 1. Réseau hydrographique fin (rivières 1 plot, îlots, bras)
- **Gain visuel attendu : le plus élevé** — restaure la lecture géographique du centre (rivières qui entourent les plaines, relient les lacs).
- **Risque technique : moyen** — extraire les canaux fins du raster de référence à 96×78 (risque de bruit : un plot ≈ largeur de rivière) ; supports sous l'eau ; pièces 1×N bleues → pavage plus fragmenté.
- **Coût en pièces : +1 à +3 %** (≈ +120 à +350), pas de nouvel élément saillant (eau affleurante, pas de C3).
- **Tests** : 0 collision/déconnexion/îlot ; liens faibles ≤ 3 ; IoU eau vs raster de référence en hausse mesurée (zone témoin) ; baselines des 8 cartes inchangées (option désactivée par défaut) ; relecture visuelle humaine sur 3 vues.
- **Critère d'abandon** : IoU eau n'augmente pas d'au moins 10 points relatifs, ou > +5 % de pièces, ou ≥ 1 nouveau lien faible, ou deux cycles sans gain visuel jugé par l'humain.

## 2. Repères construits (8–12 points d'intérêt de ≤ 25 pièces)
- **Gain visuel attendu : élevé** — transforme des pastilles en formes reconnaissables (château, tours, ponts, villes) et donne l'échelle « maquette ».
- **Risque technique : élevé** — lisibilité à 1 plot ; choix des coordonnées à valider humainement ; chaque repère ajoute des pièces exposées (C3) ; supports obligatoires.
- **Coût en pièces : +2 à +3 %** (≈ +250 à +350).
- **Tests** : validateurs (collision, support, connectivité) ; budget C3 ≤ 17 % ; aucun nouveau lien faible ; mesure du détachement (pièce unique ≤ 1 g) ; rendu avant/après par repère ; baselines inchangées.
- **Critère d'abandon** : repère non reconnaissable à la relecture humaine (2 cycles), ou C3 > 17 %, ou liens faibles nouveaux, ou > +4 % de pièces pour moins de 8 repères validés.

## 3. Texture de surface et couleur : tons, chemins, braises, désert
- **Gain visuel attendu : moyen à élevé** — casse les régions uniformes (plaine, désert, océan est, massifs gris) et ajoute les chemins et le volcan rouge.
- **Risque technique : faible à moyen** — disponibilité des couleurs (min. de sets), cohérence des teintes (ΔE), ne pas augmenter C3 : privilégier des tuiles **affleurantes** (C2).
- **Coût en pièces : 0 à +2 %**.
- **Tests** : disponibilité couleur/pièce (Rebrickable) ; part ≥ 8 tenons et nombre de couleurs par secteur mesurés avant/après ; C3 non aggravé ; baselines inchangées ; relecture humaine.
- **Critère d'abandon** : aucune réduction mesurée de la part de grandes plaques unies (≥ −5 pts) ET aucun gain visuel humain ; ou C3 en hausse > 1 pt ; ou couleur indisponible.

## Ordre conseillé
1 (rivières) → 3 (texture, sans risque structurel) → 2 (repères, plus risqué). Chaque amélioration : maximum 3 cycles ciblés ; abandon si deux essais n'apportent aucun gain mesuré.
## Conditions préalables
Accord explicite pour démarrer V17 ; aucune référence CI ne sera gelée ni mise à jour sans votre accord ; mesures structurelles V17 avec `structural_classify_v16.py` et `weaklink_v16.py` (indicateur adapté) en plus de l'ancien pourcentage.
