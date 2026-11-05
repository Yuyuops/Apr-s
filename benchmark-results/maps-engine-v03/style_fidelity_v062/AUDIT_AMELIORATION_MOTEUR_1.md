# Audit — améliorations possibles du moteur 1
Branche `research/lego-maps-v07-engine2-final` (depuis V0.6.2). Code et résultats : commit `59c06c9`. Environnement : engine 1 portable en lecture seule (`env.sh`), Python venv du moteur, rendus three.js sur maillages LDraw réels. Génération reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (6,6 s pour le 64×96).
Périmètre : lecture seule du moteur 1 appliqué aux sorties du moteur 2. **Aucune modification du moteur 1.** La phase D du cahier des charges suppose un moteur 2 stabilisé ; il ne l'est pas (NO-GO). Cet audit est donc limité aux mesures disponibles.

## Constats mesurés (13 816 pièces)
- Validateur : 0 collision, 0 déconnexion, 0 îlot, 0 non supporté, sur toutes les variantes testées. Aucun défaut de constructibilité détecté par le moteur 1.
- Fragilité : 1 053 pièces tenues par un seul tenon (390 porteuses), 928 points d'articulation. Famille `strata_body` dominante (800 points d'articulation, 357 porteuses à un tenon dans la base). 312 tuiles d'angle arrondi 25269 tenues par un seul tenon (décoratives). Pire défaillance simple : 6 pièces, 2,4 g.
- Performance : `fragility.py` environ 115 s à 13,8 k pièces ; génération 6,6 s.

## Pistes (non implémentées, gains non mesurés)
| Piste | Gain attendu | Risque |
|---|---|---|
| Recouvrement des porteuses à un tenon par une tuile voisine ou un pavage décalé (strates) | Moins de porteuses isolées (390) | Plus de pièces ; effet visuel sur le pavage à vérifier |
| Fixation des feuilles décoratives (25269, 98138) | Réduit les pièces détachables | Aucune pièce de fixation vérifiée ; risque visuel |
| Accélération de `fragility.py` (graphe incrémental) | Temps réduit sur grandes grilles | Faible |
| Notices : regroupement par couches | Moins d'étapes | Non mesuré |

## Décision
**Aucune amélioration significative et démontrable n'a été établie** dans le cadre de cette version : le moteur 1 existant est conservé. Aucune branche de correction du moteur 1 n'a été ouverte. Aucune validation physique n'est déclarée.
