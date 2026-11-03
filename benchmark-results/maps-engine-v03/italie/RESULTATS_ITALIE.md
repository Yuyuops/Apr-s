# LEGO Maps V0.3 — Italie 48×48, comparaison réelle A/B

Date : 2026-11-03. Branche : \`research/lego-maps-italie-v03-20261103\`.

## Entrée géographique vérifiable

- Natural Earth public domain, couche pays au 1:10m (Italie), commit source \`ca96624a56bd078437bca8184e78163e5039ad19\`.
- Script reproductible : \`make_italy_source.py\`, fichier produit : \`source/italie_ne_10m_style.png\`.
- Sélection du véritable polygone Italie, avec Sicile et Sardaigne, et 29 sous-polygones.
- La carte superpose des couleurs de style et des bandes artistiques Alpes/Apennins. **AUCUNE altitude réelle et aucune donnée DEM.**
- Source raster SHA-256 : \`09cb92f46c9355aba5b542ef6ef93f9e2883c53fbcf54fb734345206baa61ef4\`.

## Chaîne exécutée

Deux générations **complètes du vrai moteur V0.3**, \`full\`, même image source :
- Finition A : \`--finish A --n 48 --frame 2\`, tenons apparents.
- Finition B : \`--finish B --n 48 --frame 2\`, eau partiellement lissée / finition cadre.

Dimensions totales : 52×52 tenons, **416×416 mm**, épaisseur calculée 19,2 mm.

| Indicateur | A | B |
|---|---:|---:|
| Pièces | 371 | 656 |
| Références pièce×couleur | 57 | 75 |
| Étapes numériques | 28 | 45 |
| Notice PDF | 31 pages | 48 pages |
| Masse estimée (hypothèses moteur) | 2 038 g | 2 126 g |
| Porteuses critiques avant optimiseur | 20 | 32 |
| Porteuses critiques après optimiseur | **18** | **20** |
| Porteuses faibles finales | 43 | 74 |
| Pièces supportées par un seul tenon | 48 | 73 |

**Validation numérique des deux modèles :** zéro collision, zéro pièce déconnectée, zéro îlot, zéro pose sans appui, zéro tenon bloqué ; 371/656 pièces concordantes entre \`parts.json\`, \`map.ldr\` et \`parts_list.csv\`. Le viewer HTML, les rendus PNG et les notices PDF sont générés, vérifiés présents et non vides.

**Verdict : Italie numérique générée AVEC LIMITATIONS.** Les 18/20 porteuses critiques résiduelles sont un risque majeur de manipulation ou d'accrochage, aucune construction ni résistance réelles n'ont été vérifiées. Ce sont des métriques de modèle, pas des essais physiques. Prix et stocks Briquestore non vérifiés (HTTP 202).

## Qualité visuelle / comparaison à l'image IA

- La géographie de la botte, la Sicile et la Sardaigne est reconnaissable.
- La version B est plus propre visuellement sur la mer, mais représente +285 pièces, davantage de porteuses critiques et davantage de pièces tenues par un seul tenon.
- La carte reste **loin du tableau décoratif IA** : pas de monuments, pas de rose des vents, pas de plaque typographique italienne, ni relief géographique réel, ni cadre doré; ces détails ne sont pas générés par la V0.3 actuelle.
- 48×48 tenons est insuffisant pour garder tous les détroits, côtes, petites îles et détails fins. La mer occupe une large part de la surface; un cadrage portrait ou une grille plus fine serait utile.

## Traçabilité exacte de l'exécution

Run : https://github.com/Yuyuops/Apr-s/actions/runs/41720299673

Artefact (source + les deux LDraw, nomenclatures, images, viewers, PDFs) :
https://github.com/Yuyuops/Apr-s/actions/runs/41720299673/artifacts/13272281921

Les deux exécutions \`full\` sont marquées **SUCCESS**. Le dernier script de contrôle d'assemblage a signalé un \`TypeError\` : il attendait \`collisions.pairs\`, alors que \`validation_resume.json\` expose déjà \`collisions\` sous forme d'entier. Le workflow GitHub a été corrigé (mais **non relancé**) ; une vérification locale indépendante de l'artefact récupéré a confirmé l'absence de collisions, d'îlots, de pièces déconnectées et les concordances LDraw/BOM ci-dessus. Par transparence, le run GitHub dans son ensemble apparaît FAIL à cause de ce script de contrôle, **pas** des générateurs.

Aucun achat. Aucune modification du moteur 1. Aucune fusion \`main\`.

## Décision proposée

Conserver ces résultats comme benchmark Italie. Ne pas passer directement à une version commerciale. Pour rivaliser avec l'image illustrative, tester d'abord un plus grand format / un cadrage adapté, puis travailler les reliefs, les monuments simplifiés et le cadre comme modules explicites. La résistance réelle des supports et la notice physique sont à traiter avant tout achat ou accrochage.
