# Démonstrateur Hyrule — généré ; rendu NON convaincant avec ce style
Branche `research/lego-maps-v09-prototype-hyrule`. Style Premium Noyer/Or/Lagon (`premium_noyer_or_lagon_c2i`), seuls ajustements : titre « HYRULE » (option `allow_subject_land`, voir plus bas). **Cas à part : démonstrateur visuel, aucune validation géographique ni multi-cartes du moteur.**

## Source (documentée)
1. **Dépôt** : aucune carte Hyrule (uniquement des listes de figurines). **Fichiers du projet** : aucun.
2. **Source utilisée : l'image que vous avez fournie** dans la conversation : un rendu 3D oblique, 1920 × 1080 px JPEG, d'un modèle LEGO de la carte de *Breath of the Wild* (titre « The Legend of Zelda — Breath of the Wild »). Auteur et licence du modèle : **inconnus de moi**. Empreinte SHA-256 (16 premiers caractères) : `4b9c7b22e3b461c0`. **L'image n'est pas versionnée** (je ne redistribue pas une œuvre tierce) ; seul le masque dérivé l'est.
3. Une affiche Wikipédia (« Map of Hyrule Puzzle ») avait été écartée plus tôt : œuvre sous droit sans trait de côte.

## Traitements appliqués (`hyrule_mask_from_render.py`, aucune géographie ajoutée)
1. **Rectification de perspective** : homographie à partir de **4 coins du plateau mesurés à la main** sur une grille posée sur l'image : (322,48), (1615,48), (1668,812), (163,812). Sortie carrée 960 × 960 px.
2. **Segmentation par couleur** : plaques bleues (teinte 190–245°, saturation > 0,30, luminosité > 0,28) = **mer** ; plaques sable pâles (teinte 28–62°, saturation 0,10–0,60, luminosité > 0,66), régions ≥ 40 tenons² = **désert**, rendu comme terre plate de la classe « terre étrangère » du style ; **tout le reste du plateau = terre**. Lissage gaussien, retrait des poussières de moins de 1,5 tenon², remplissage des trous du désert.
3. **Grille 80 × 80 tenons**, `sub = 8`. Le masque (`compositions/hyrule_mask_80x80.png`) alimente le moteur par la nouvelle clé de composition `mask_png`.
Résultat : mer 6,1 % de la surface, désert 10,5 %, terre le reste ; 1 masse terrestre, 11 plans d'eau détectés.

## Hypothèses prises (toutes discutables)
- **Plateau carré** : la proportion réelle du modèle photographié est inconnue ; si elle ne l'est pas, la carte est déformée.
- Les 4 coins sont mesurés à l'œil sur une image en perspective, avec une erreur de quelques pixels (≈ 1 tenon).
- « Bleu = mer » : les lacs intérieurs de la source apparaissent donc comme de petits plans d'eau ; les reliefs (volcan, neiges, forêts) sont **ignorés** (aucune carte de hauteur extraite).
- « Sable = désert » : classe visuelle, non un territoire.
- Titre : la carte n'a aucune zone plate libre ; option générique `allow_subject_land` (lettres sur la terre, zone entièrement terrestre, rien d'autre modifié), titre « HYRULE » en haut.

## Résultat
| | |
|---|---|
| Pièces / références | **16 721 / 99** |
| Dimensions | 704 × 704 mm (88 × 88 tenons avec cadre), 76,8 mm de haut |
| Validation moteur 1 | 0 collision, 0 déconnectée, 0 îlot, 0 non supportée ; catalogue complet ; 0 substitution |
| Concordance LDraw / nomenclature / plan | oui (550 étapes) ; notice tableau générable |
| Fragilité indicative | 431 pièces à un tenon (241 porteuses), 437 points d'articulation, pire défaillance 3 pièces / 6,4 g (cadre) |
Fichiers : `livraison_v09/hyrule/` (LDraw, `parts_list.csv`, `rebrickable_import.csv`, métriques, fragilité, rendus face / trois-quarts / zoom, masque). Le LDraw est régénéré par la CI (`regen_deliverables.sh`).

## Le rendu est-il convaincant ? **Non.**
- Le style Premium repose sur **une côte et des strates de profondeur** : ici la mer ne couvre que 6 % de la carte, le style donne un **grand aplat brun** avec un coin de sable, un liseré d'eau à l'est et au sud. La carte source tire son identité de ses **biomes** (neige, désert, forêt, volcan, lacs), que ce pipeline à deux classes ne représente pas.
- Le cadre noyer, les filets or, les médaillons et le titre fonctionnent bien, mais l'ensemble n'est **pas reconnaissable comme Hyrule** sans la source à côté (comparaison faite ; non versionnée).
- Conclusion produit : le style actuel est adapté à **des géographies avec une mer** ; une carte fictive terrestre demanderait un **mode « biomes + relief »** (classes de terrain colorées, carte de hauteur extraite), qui est un chantier du moteur 2, non lancé ici.

## Limites et à ne pas faire
Pas de validation multi-cartes ; image source de droits inconnus ; carte et proportions approximatives ; aucune interprétation du relief ; aucune notice illustrée ; aucun prix ni test physique.
