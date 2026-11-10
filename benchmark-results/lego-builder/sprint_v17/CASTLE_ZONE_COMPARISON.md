# Sprint V17 — Zone du château : Référence LEGO / V16 / V17

Zone pilote D : 32×32 plots, rangée 18–49, colonne 30–61 de la grille V16 (`data/zone_D_classes.*`), même style, même relief et mêmes données que V16 ; seule différence : le manifeste d'objets (`castle_zone_objects.json`) + remplacement de la règle d'arbres V16 par des arbres assemblés. Aucune note ni GO artistique : **validation visuelle humaine requise**.

## Planches (mêmes zones, mêmes caméras V16/V17)
| Vue | Fichier |
|---|---|
| Dessus (référence / V16 / V17) | `renders/compare_top_ref_V16_V17.jpg` |
| Trois-quarts (référence complète / V16 / V17) | `renders/compare_threequarter_ref_V16_V17.jpg` |
| Gros plan château (référence / V16 / V17) | `renders/compare_castle_closeup_ref_V16_V17.jpg` |
| Ponts, chemins, végétation (V16 / V17) | `renders/compare_bridges_V16_V17.jpg` |
| Hauteurs, vue latérale (V16 / V17) | `renders/compare_side_heights_V16_V17.jpg` |
| Vues séparées | `renders/zoneD_{V16,V17}_{top,trois_quarts,lateral,chateau,ponts}.jpg` |
Pas de vue latérale ni de gros plan de la référence : ces deux colonnes manquent (limite documentée).

## Ce qui change, visiblement (V16 → V17)
- **Constructions en volume** : un château à tourelles (hauteur 18 plaques), 4 tours rondes, 4 ponts, qui n'existaient pas en V16 (aucun volume > relief).
- **Rivières** : deux bras fins d'un plot qui traversent la plaine et que franchissent les ponts ; chaussée grise au sud du château.
- **Végétation** : 37 arbres assemblés (couronnes rondes, conifères, petits) au lieu de troncs 1×1 identiques ; 4 rochers.
- Hauteur maximale de la zone : 57,6 mm → 76,8 mm.

## Ce qui reste insuffisant (comparaison à la référence)
- **Le château V17 est trop massif et trop clair** : murs gris à créneaux, quatre tourelles ; la référence montre une silhouette sombre, élancée, à nombreuses flèches et pointes roses/magenta, avec une douve circulaire. Il lit comme « un château », pas encore comme *le château d'Hyrule*.
- **Rivières** : trop fines et d'un bleu vif ; la référence les montre de 1 à 2 plots, bleu-gris foncé, en réseau qui entoure des îlots.
- **Densité de détails** : la référence a des centaines de petits objets (arbustes, fleurs en grappes, ruines, enclos, chemins) ; la plaine V17 reste une grande surface verte lisse.
- **Chemins** : un seul tronçon ; la référence a des routes et escaliers.
- **Positions** : estimées à ± 1,5 plot ; la douve ronde du château et la plupart des petites constructions ne sont pas reproduites.
- Hauteurs et profils : choix de la bibliothèque, non mesurés sur la référence (aucune vue latérale).

## Cycles (maximum 3)
1. Première construction : château, 4 tours, 4 ponts, rivières niveau 1 (trop profondes : tranchées sombres sous les ponts), arbres majoritairement coniques.
2. Rivières au niveau 2 (affleurantes), arbres plutôt ronds ; reconstruction, validation, structure. **Retenu** (`work17/D_v17b`).
3. **Non utilisé** : je n'ai pas lancé de troisième cycle, faute d'un gain mesurable attendu sans nouvelle donnée de référence (la limite est la qualité des objets, voir `FINAL_VERDICT.md`).

## Coût
Pièces : 1 750 (V16) → 1 950 (V17), **+11 %** dont 112 pièces d'objets (château 31, tours 12, ponts 4, rochers 12, arbres 53) ; le reste vient des rivières et du remplacement du pavage autour des objets. Le but n'est pas le nombre de pièces ; ce coût est signalé.
