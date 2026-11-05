# Validation technique (Italia Prestige 64×96)
Branche `research/lego-maps-v07-engine2-final` (depuis V0.6.2). Code et résultats : commit `59c06c9`. Environnement : engine 1 portable en lecture seule (`env.sh`), Python venv du moteur, rendus three.js sur maillages LDraw réels. Génération reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (6,6 s pour le 64×96).
Contrôles : validateur indépendant du moteur 1 (`check_render.py`), `verify_bom.py`, `fragility.py`. Les résultats numériques ne sont pas une preuve de résistance physique (`physical_test: false`).

| Variante | Pièces | Réf. | Collisions | Déconnectées | Îlots | Non supportées | Substitutions couleur |
|---|---:|---:|---:|---:|---:|---:|---:|
| base V0.6.2 (reconstruite) | 13 826 | 124 | 0 | 0 | 0 | 0 | 0 |
| **candidat V0.7 (cadre C)** | **13 816** | **124** | **0** | **0** | **0** | **0** | **0** |
| palette D (rejetée) | 14 818 | 122 | 0 | 0 | 0 | 0 | 0 |
| zones flancs et cadres (24 variantes locales) | voir `results/` | | 0 | 0 | 0 | 0 | 0 |

Concordance modèle / inventaire : `verify_bom` du candidat : 13 816 pièces, 124 références, tous les fichiers .dat existent, couleurs valides, 0 couple non catalogué. Les notices (PDF) n'ont pas été régénérées pour le candidat (rejeté faute de score) : **non vérifiée**.

## Fragilité indicative (base V0.6.1 → candidat V0.7)
| Mesure | Base | Candidat |
|---|---:|---:|
| Pièces tenues par un seul tenon | 1 004 | 1 053 |
| dont feuilles décoratives | 619 | 663 |
| dont porteuses | 385 | 390 |
| Points d'articulation avec perte | 899 | 928 |
| Pire défaillance simple | 6 pièces, 2,4 g | 6 pièces, 2,4 g |

Les 48 tuiles rondes dorées 98138 du médaillon sont des feuilles tenues par un seul tenon (décoratives). Elles sont plates et sans pièce portée, mais vulnérables à un arrachement : à signaler à l'assemblage. Les 5 porteuses supplémentaires viennent du réagencement du pavage du cadre.
Temps : génération 6,6 s ; `fragility.py` environ 115 s sur 13 816 pièces.
Limites : aucun essai physique, aucun prix ni stock vérifié.
