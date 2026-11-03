# Verdict LEGO Maps V0 : **V0 AVEC LIMITATIONS**

Le flux image → LEGO → LDraw / nomenclature / rendus / viewer / notice PDF est complet, cohérent et vérifié numériquement sur deux cartes, sans donnée inventée :
* île témoin 2.5D : 153 pièces, 9 × 1×1 (5,9 %), 0 collision, 0 pièce déconnectée, 256 × 256 × 22,4 mm, 15 étapes par région et couche, IoU de cellules 0,905 (frontières F1 1,0), hauteurs 98,7 % identiques à l'oracle ;
* généralisation `test_3_zones` : classes correctes (IoU de cellules 1,0), 119 pièces, 0 collision ;
* essai 1 aveugle archivé (commit 7fd35eb) avant toute correction ; deux corrections ensuite, effet mesuré (1×1 16 → 9, rivière continue, IoU de cellules −0,03).

Pas « V0 VALIDÉ » car des limites mesurées subsistent : ΔE de couleur élevé (terre 18,5, forêt 21,2, sommet 28,7 ; moyenne 12,95) ; classes minces peu précises au pixel (rivière 0,41, route 0,46, village 0,25) ; 9 plaques tenues par un seul tenon ; rigidité seulement indicative (aucun essai physique, aucune fixation murale déclarée sûre) ; prix et stocks **non vérifiés** (Briquestore : accès non exploitable, valeurs `null`) ; reconnaissance validée sur deux cartes synthétiques seulement.
Pas « À CORRIGER » : aucun échec de génération ni d'assemblage, aucune donnée inventée.

Décisions attendues avant d'aller plus loin : relief (style de hauteurs, village / routes), palette (accepter un ΔE plus élevé ou autoriser le partage de couleurs entre classes proches), finition (tuiles / cadre), vérification manuelle des prix et stocks chez Briquestore.
