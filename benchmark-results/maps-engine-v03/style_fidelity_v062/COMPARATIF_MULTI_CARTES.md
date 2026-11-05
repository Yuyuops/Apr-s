# Comparatif multi-cartes
Branche `research/lego-maps-v07-engine2-final` (depuis V0.6.2). Code et résultats : commit `59c06c9`. Environnement : engine 1 portable en lecture seule (`env.sh`), Python venv du moteur, rendus three.js sur maillages LDraw réels. Génération reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (6,6 s pour le 64×96).

**Statut : NON EXÉCUTÉ.** La phase B ne démarre que lorsque l'Italia Prestige 64×96 atteint 20/25 ; le score est 15/25. Aucune carte Écosse, Japon ou Royaume-Uni n'a été générée dans cette version, et aucune note ni mesure n'est inventée.

| Carte | État | Note |
|---|---|---|
| Italie 64×96 | Générée, validée techniquement (0/0/0/0) | 15/25, **échec** du seuil |
| Écosse | Non générée | — |
| Japon | Non générée | — |
| Royaume-Uni | Non générée (carte) ; la recherche de figurines UK existe mais n'est pas une carte | — |

Décision : **NO-GO** pour la généralisation. Prérequis avant de la lancer : atteindre 20/25 sur l'Italie par un gain démontré sur la silhouette ou la couleur (voir ROADMAP_MOTEURS.md).
