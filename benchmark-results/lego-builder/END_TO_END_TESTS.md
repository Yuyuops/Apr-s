# Tests de bout en bout (A à D)
Branche `research/lego-builder-unified`. Résultats archivés dans `e2e_results/` (manifestes, analyses, LDraw, nomenclatures, validations, rendus ; **les images sources de tiers ne sont pas redistribuées** : le manifeste en garde le SHA-256). Script de reproduction : `tests/run_e2e.sh`. Tous les modèles : validés au niveau « existence catalogue » seulement ; **ni stock, ni prix, ni essai physique**.

## Test A : Italie (données géographiques)
Commande : `lego_builder geo --composition italia_portrait_64x96.json --style premium_noyer_or_lagon_c2i.json`.
- **LDraw identique octet à octet** à la référence (SHA-256 `17d9bdc6…`) ; nomenclature identique à la livraison V0.8 (13 633 pièces, 111 références).
- Validations : 0 collision, 0 pièce déconnectée, 0 îlot, 0 non supporté, 0 substitution ; concordance LDraw / nomenclature / plan (492 étapes) ; 97 s.
- Après la correction générique du cadre faite pendant cette mission (voir D), l'Italie reste identique. **Les 7 autres modèles de la CI n'ont pas été rejoués localement après cette correction** : la CI de la branche les revérifie (résultat dans `FINAL_VERDICT.md`).

## Test B : Hyrule (image seule, sans masque ni JSON)
Commande : `lego_builder run src.jpg --out … --size-mm 400 --title Hyrule` (400 mm = « 40 cm »).
- Analyse : carte 2,5D, planche encadrée détectée, perspective rectifiée automatiquement.
- **Données générées sans intervention** : coins, classes, palette, composition, style, aperçu.
- Parcours complet en **32 s** : grille 42 × 42, **3 245 pièces, 120 références**, validé (0/0/0/0, catalogue complet, plan de 122 étapes concordant).
- Comparaison avec la V1.0 (masque réglé à la main, 704 mm, `--size-mm 704`) :
| | V1.0 manuel | Auto |
|---|---:|---:|
| Pièces / références | 10 682 / 134 | 10 699 / 137 |
| Eau, herbe, forêt (part de surface) | 9,9 %, 21,6 %, 9,0 % | 15,0 %, 22,0 %, 8,7 % |
| Roche, désert, pierre, neige | 18,5 %, 12,8 %, 21,7 %, 6,5 % | 19,8 %, 10,8 %, 17,9 %, 5,9 % |
| Pièces à un tenon (dont porteuses) | 1 898 (1 050) | 2 031 (1 201) |
| Points d'articulation ; pire défaillance | 1 532 ; 4,4 g (strates) | 1 582 ; 11,2 g (cadre) |
- **Accord pixel à pixel** des classes avec le masque manuel : **0,58** à position égale, **0,83** si l'on autorise un décalage de 4 tenons. La classification est équivalente ; c'est le **recalage** qui diffère (la détection automatique des coins s'écarte de 5 % de la largeur environ des coins mesurés à la main).
- Les **proportions réelles** du plateau sont inconnues : carré supposé (signalé dans le manifeste).

## Test C : Paco (GLB)
Commande : `lego_builder run paco.glb --out … --size-mm 400`.
- Analyse : sculpture 3D, 231 740 faces, étanche, couleurs par sommets ; sujet **connu** (empreinte) donc configuration validée.
- Génération par le moteur 1 existant (`lego_run.py`) : 125 s.
- **LDraw identique octet à octet** au modèle accepté V12.1 (`22_color_structural_regression/modeles/paco_V121_A_palette_V12/paco_brut.ldr`, SHA-256 `9d07c041…`) : 3 193 pièces, 89 références. Ce modèle **n'a pas été remplacé**.
- Validation du moteur 1 : 0 collision, 0 tenon bloqué, 8 cas faibles (identique à la recette acceptée), catalogue complet.
- Rendus LEGO face à face avec le GLB de référence : `e2e_results/C_paco/lego_vs_glb.png`.
- **Notice hiérarchique : non construite dans ce test.** L'étape `notice` du moteur 1 n'avait jamais été exécutée dans les installations propres (elle s'appuie sur les calculs d'oreilles) ; après plus de 20 minutes de calcul sur 3 processus, je l'ai arrêtée. Elle est disponible en option (`build --notice`) ; la notice acceptée de V12.1 reste dans `22_color_structural_regression/notices/`.
- Un GLB **inconnu** n'a pas été testé : il n'existe pas d'autre GLB dans le dépôt, et la reconstruction photos → GLB n'a pas été exécutée.

## Test D : nouvelle image de carte
Image : `ref_B_atlas_natural_UK.webp` (rendu LEGO d'une carte du Royaume-Uni, fond clair, planche encadrée de brun). Elle vient du dépôt (référence de style de la V0.6) et **n'a servi à aucun réglage de classification ou de détection avant ce test**. Une image extérieure n'a pas pu être téléchargée (Wikimedia limité en débit, NASA inaccessible).
Première exécution sans modification : **trois défauts trouvés**, corrigés de façon générique, puis test rejoué :
1. L'analyse classait l'image « indéterminée » (l'eau bleu pâle n'était pas reconnue) : seuil d'eau abaissé.
2. Le fond clair n'était pas géré : détection de planche sur fond clair uniforme ajoutée.
3. Avec une proportion non carrée, le **générateur plantait** (`random.choices` sur liste vide) : les filets dorés du cadre supposaient des longueurs paires ; correction générique (carreau rond doré 1×1 catalogué en fin de filet).
Honnêteté : ces corrections ont été faites **après** avoir vu l'échec, donc le test D n'est plus un test aveugle ; l'Italie reste identique après la correction 3, et les parts de classes de Hyrule ont bougé (eau 11 % → 15 %).
Résultat final : `run` en une commande (**30 s**), **validé** : 3 374 pièces, 101 références (proportion carrée par défaut) ; avec `--aspect 0.6` : 2 301 pièces, 86 références.
**Fidélité : faible à moyenne.** L'île est reconnaissable (terre verte sur eau bleue, sommets bruns) mais : la planche rectifiée est rognée, l'écume blanche de la mer est parfois classée « neige » sur les côtes, la bande du cadre est classée comme terrain, les collines kaki deviennent de l'herbe, les proportions sont supposées. La détection des coins par l'enveloppe convexe est approximative.

## Synthèse
| Test | Parcours sans intervention | Résultat technique | Fidélité |
|---|---|---|---|
| A Italie | oui | identique à la référence | exacte (même modèle) |
| B Hyrule | oui (une commande) | validé, proche de la V1.0 | classes équivalentes, recalage approximatif |
| C Paco | oui (une commande) | identique au modèle accepté | celle du modèle accepté |
| D nouvelle carte | oui, après 3 corrections | validé | faible à moyenne |
