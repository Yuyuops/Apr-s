# Sprint V13 — Verdict final : **GO limité**

Rien n'a été fusionné dans `main` ; aucune référence validée n'a été modifiée ; rien acheté ; aucune fabrication ; Bambu Studio non utilisé (BLOCKED, non installable ici).

## 1. Nos modèles sont-ils assez beaux pour être vendus ?
- **Italy Premium : oui, sous réserve.** 19 → **21/25** (3 cycles, grille inchangée, valid. indépendante PASS, 13 354 pièces, stabilité meilleure que la baseline, build reproductible). Score auto-attribué : à confirmer par un regard humain avant toute vente. Défauts restants : relief par paliers (pas de dégradé), taupe terne, cadre/typographie non améliorés. Le style C3 n'est pas encore gelé par un SHA en CI.
- **Paco : acceptable, pas amélioré.** V12.1 conservé : ΔE 15,5 (plancher palette atteint), bouche et lèvre perfectibles (limite moteur : lèvre courbe non implémentée). Vendable comme pièce « de démonstration artisanale », pas comme réplique fidèle.
- Beagle : non touché, non régressé en CI.

## 2. Les modules sont-ils fidèles et prêts pour un essai d'impression ?
**Prêts pour un essai limité (coupon + un module), pas pour une fabrication complète.**
- Corrigés : tenons de liaison désormais exportés ; 109 pièces Paco ignorées silencieusement réintégrées ; formes courbes (pentes, ronds, quarts de rond) préservées par enveloppe convexe (preuves visuelles Paco tête et Hyrule côte) ; tuiles à imprimer retournées.
- Mesuré : tout est étanche, en mm, dans le plateau 256 mm (Hyrule 240 mm : marge 16 mm), tranchable par un second slicer.
- Non résolu : concavités remplies et plots de pentes omis ; avec supports, conflits de chemins entre couleurs et masse ×1,9 ; estimations de temps du dépôt sous-évaluées (×2,5 à ×5) → corriger avant tout devis ; Bambu Studio non testé ; affectation des couleurs/AMS inconnue.

## 3. Quelles preuves manquent encore pour commercialiser ?
1. **Coupon de tolérance imprimé et mesuré** (jeu plots/tube, tenons, détails courbes) — sans lui, la compatibilité FDM n'est pas démontrée (*décision humaine : imprimer*).
2. **Import + tranchage dans Bambu Studio** avec le vrai modèle d'imprimante : dimensions, temps, masse, supports, changements de couleur (*humain*, procédure dans `BAMBU_READINESS.md`).
3. **Un sujet inédit à partir de quatre photos** avec le protocole C (*entrée humaine : fournir les photos*) — la généralisation n'est pas prouvée.
4. **Validation visuelle humaine** d'Italy C3 (et décision d'en faire une référence CI bloquante).
5. **Prix et stocks réels** (`prices.template.csv`) pour toute offre chiffrée ; temps d'impression réels (mesure sur imprimante).
6. Résolution des conflits couleurs/supports et du remplissage des concavités si un module avec arches ou détails creux est vendu.

**Décisions nécessaires de votre part** : (a) imprimer le coupon ? (b) fournir les 4 photos d'un nouveau sujet ; (c) valider visuellement Italy C3 ; (d) fournir/valider une imprimante Bambu cible pour le tranchage.
