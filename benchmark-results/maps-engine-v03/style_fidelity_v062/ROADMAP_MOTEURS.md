# Feuille de route des moteurs
Branche `research/lego-maps-v07-engine2-final` (depuis V0.6.2). Code et résultats : commit `59c06c9`. Environnement : engine 1 portable en lecture seule (`env.sh`), Python venv du moteur, rendus three.js sur maillages LDraw réels. Génération reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (6,6 s pour le 64×96).

## Moteur 2 — bloqué à 15/25 (NO-GO)
Pour atteindre 20/25 il faut un gain démontré d'au moins un critère à 4/5 sans aucun < 3 :
1. **Silhouette** : vérifier et cataloguer une pièce de coin concave réelle (par exemple 93273) avec orientation et connexions, puis tester un lissage de rasterisation. Aucune pièce candidate n'est vérifiée aujourd'hui.
2. **Couleurs** : trouver un moyen de rendre le menthe sans pavage partiel d'Aqua (par exemple vérifier d'autres couples pièce/couleur catalogués, sans supposer leur disponibilité).
3. **Finition** : ornements d'angle en volutes avec de vraies pièces ; lettres du titre relevées.
4. Phase B (Écosse, Japon, Royaume-Uni) seulement après 20/25 réel sur l'Italie.
5. Phase C (nettoyage, centralisation, notices automatiques, RC1) seulement après validation multi-cartes.

## Moteur 1
Conservé tel quel. Pistes de l'audit : porteuses à un tenon, fixation des feuilles, performance de `fragility.py`. À reprendre quand le moteur 2 sera stabilisé.

## Hors périmètre
Figurines : module isolé, désactivé par défaut. Pas d'achat, pas de fusion dans `main`.
