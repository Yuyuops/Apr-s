# Démonstrateur Hyrule — BLOQUÉ (aucune source utilisable) ; pipeline adapté
Branche `research/lego-maps-v09-prototype-hyrule` (base : V0.8 `research/lego-maps-premium-feasible-v08` + correction moteur 1 `research/lego-maps-engine1-fragility-v08`). Style gelé : Premium Noyer/Or/Lagon (`premium_noyer_or_lagon_c2i`), note de référence **19/25 inchangée**. Régénération complète : `style_fidelity_v062/regen_deliverables.sh OUT --render --pdf`.

## Résultat
**Aucune carte Hyrule n'a été générée.** Je n'ai trouvé aucune source de géographie Hyrule (terre/mer ou relief) utilisable sans l'inventer. La règle « pas d'invention de données source » est respectée : la piste est arrêtée et documentée.

## Recherche de source, dans l'ordre demandé
1. **Dépôt** : `git ls-files` et `git grep` : seuls des fichiers du module figurines mentionnent Hyrule (`figures/themes/hyrule.json`, `hyrule_candidates.json`, `hyrule_selection.png`). Ce sont des listes de minifigurines du catalogue Rebrickable, **aucune carte**.
2. **Fichiers fournis dans le projet** : aucun.
3. **Source externe** :
   - Wikis Zelda (`zelda.fandom.com`, `zeldadungeon.net`) : accès refusé (HTTP 403).
   - Wikimedia Commons / API Wikipédia : limités (429) ; la page Wikipédia « Hyrule » reste accessible.
   - La seule image de carte trouvée : *MapOfHyrulePuzzle.jpg* (page Wikipédia « Hyrule », légende « A map of Hyrule depicted in *The Legend of Zelda Collector's Puzzle* »), 385×259 px, JPEG. Hash non conservé, image **non versionnée**.

## Pourquoi elle est inutilisable
- C'est une **illustration d'affiche sur parchemin** (encre sépia, rose des vents, texte), sans trait de côte : pas de terre/mer à extraire. Toute côte, île ou relief serait **tracé par moi**, donc inventé.
- Image sous droit d'auteur (usage « non libre » sur Wikipédia, limité à l'article). Je ne dérive pas un modèle de cette œuvre sans autorisation claire.
- Résolution trop faible (385 px de large).
Je n'ai pas converti la densité d'encre en relief : cela produirait un « relief de dessin » sans rapport avec une géographie, ce qui serait trompeur.

## Adaptation générique du pipeline (faite, testée)
Pour qu'une source valide soit utilisable dès qu'elle existe : `geodata.rasterise_mask` et la clé de composition `"mask_png"` (image en niveaux de gris : ≥ 192 terre du sujet, 64–191 terre étrangère, sinon mer). Aucune géographie n'est créée par le code.
**Test d'équivalence** : le masque exporté depuis le raster réel de l'Italie, reconstruit via `mask_png`, donne un LDraw **identique octet à octet** au modèle Italie V0.8 (13 633 pièces, 111 références).

## Ce qu'il faut pour débloquer
Au choix : (a) un PNG terre/mer (et éventuellement carte de hauteur) de Hyrule que vous fournissez ou dont vous confirmez les droits ; (b) votre accord explicite pour un tracé schématique **de ma main**, clairement étiqueté « interprétation », sans prétention de fidélité. Avec l'un d'eux : `build_style.py styles/premium_noyer_or_lagon_c2i.json <composition avec mask_png> OUT`, titre « HYRULE » (lettres H, Y, R, U, L, E déjà dans la police).

## Verdict sur la question produit
**Non évalué** : aucun rendu Hyrule n'existe ; je ne conclus rien sur le caractère « désirable » du style sur une carte fantasy.
