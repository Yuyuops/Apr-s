# LEGO Maps V0.5 — démonstrateur réel, premier verdict

## Objectif de qualité, arrêté

- Format final d'étude : **128 × 128 tenons**, 1 024 × 1 024 mm hors cadre, 1 056 × 1 056 mm avec deux tenons de bordure.
- Enveloppe de conception exploratoire : **10 000 à 25 000 pièces**, non déduite d'une nomenclature finale et non vérifiée commercialement. La qualité visuelle est prioritaire, puis le coût sera étudié avec la taille.
- Un grand modèle n'est **pas lancé** avant preuve de deux modules réutilisables : montagne réaliste et monument reconnaissable.

## Génération et contrôle réellement effectués

- Branche : `research/lego-maps-italie-v05-quality-first`.
- GitHub Actions, passage réussi : https://github.com/Yuyuops/Apr-s/actions/runs/41794997751
- Artéfact numérique LDraw, BOM, vues PNG, JSON : https://github.com/Yuyuops/Apr-s/actions/runs/41794997751/artifacts/13304951849
- Source : `prototype_diorama.py`.
- Démonstrateur technique : **48 × 32 tenons** (38,4 × 25,6 cm), **707 pièces**, **17 couples pièce/couleur**, **18 colonnes de Colisée**, six ouvertures liées par linteaux, montagne à deux sommets, 5,76 cm de relief au-dessus de la mer.
- **Validateur moteur 1 :** 0 collision, 0 pièce déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué.
- Quantités exactes : 707 éléments dans JSON, LDraw et nomenclature.

## Bug technique résolu

1. Premier test : 44 collisions, 107 éléments déconnectés. Le repère de la véritable pente LEGO `3039` est décalé de **demi-tenon** par rapport aux pièces rectangulaires utilisées jusque-là.
2. Correction de l'offset local LDraw selon la rotation : 0 collision, 0 déconnexion, mais 105 placements impossibles dans la séquence initiale.
3. Tri des placements par niveau de montage (avec les linteaux avant les colonnes supérieures) : **toutes les validations numériques passent**.

## Jugement visuel — PAS ENCORE GO ESTHÉTIQUE

Les vrais rendus LDraw `renders/face.png` et `renders/trois_quarts.png` prouvent :
- une montagne véritablement volumétrique, avec briques de pente ;
- une structure d'amphithéâtre multi-niveaux avec de vraies ouvertures et un modèle constructible numériquement.

Mais la montagne est encore un empilement simplifié, sans crêtes fines ni végétation ; la miniature ne ressemble **pas suffisamment** au Colisée sans explication. L'ensemble n'est pas encore comparable à la qualité du visuel IA cible. Le rendu est une **preuve d'architecture**, pas une validation artistique.

**Verdict : démonstrateur numérique valide, GO vers une deuxième itération artistique des modules ; NO-GO pour fabriquer l'Italie complète ou acheter des pièces.**

## Étape technique nécessaire

1. Définir un système d'assemblage d'arches réelles, petites fenêtres répétées, gradins ovales et murs courbes en LDraw (validation structurelle maintenue).
2. Introduire des microstructures de montagne (petites slopes, angles, cimes et végétation) et non seulement du relief par grosse grille.
3. Comparer les deux modules en gros plans, sans légende, face et trois-quarts.
4. Ensuite seulement : vrai DEM, composition des sous-modèles sur carte Natural Earth de 128², cadre et palette, sans perdre l'optimisation du pavage.
5. Si les prototypes ne deviennent pas reconnaissables après deux itérations justifiées, reconsidérer l'architecture des sous-modèles plutôt que gonfler le nombre de pièces.

**Aucun test physique, prix ou stock validé ; aucun achat ; moteur 1 inchangé ; aucune fusion dans main.**
