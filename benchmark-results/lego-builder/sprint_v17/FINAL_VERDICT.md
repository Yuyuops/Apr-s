# Sprint V17 — Verdict final

## Ce qui a été fait (preuves dans le dossier)
1. **Référence** : MOC-193441 identifié (Galaxy333, ≈ 14 876 pièces) et rapproché de la photographie jointe ; **page Rebrickable inaccessible** (403 Cloudflare / 402 payant, non contournés), **aucun fichier 3D ni instructions accessibles gratuitement** (PDF payant, non acheté). Vues réellement disponibles : 1 dessus + 3 trois-quarts ; ni latérale ni gros plans (`REFERENCE_AUDIT.md`).
2. **Objets** identifiés pour la zone du château : château, 4 tours, ≈ 5 ponts (4 reproduits), 2 rivières, chaussée, arbres, rochers ; observé / estimé séparés (`MULTIVIEW_ANALYSIS.md`).
3. **Composants réutilisés** : Maps V16 (raster de classes B16, tiler, relief, détails, validation), manifeste et analyse sémantique V15 (mêmes classes), validateur indépendant et BOM du moteur, outils de structure V16 ; **nouveau** : bibliothèque d'objets paramétriques + manifeste (générique, désactivée par défaut). Non utilisés : sculptures et Photos→3D (pas adaptés à de petits objets paramétriques à cette échelle ; un type `sculpture` pourrait poser un sous-modèle LDraw : V18).
4. **Zone du château reconstruite** : volumes réels (château 31 pièces, tours, ponts, 37 arbres, rochers), rivières et chaussée ; 1 750 → 1 950 pièces (+11 %).
5. **Comparaison** Référence / V16 / V17 : dessus, trois-quarts, gros plan château, ponts, hauteurs (`renders/`).
6. **Technique** : 0 collision / 0 déconnectée / 0 îlot / 0 non supportée ; BOM valide ; 12 assemblages validés individuellement ; reproductible (SHA-256 identique) ; fragilité porteuse séparée de la décorative ; 8 baselines, Italie, Paco, Beagle, unitaires **identiques / PASS** ; Photos→3D **BLOCKED** (quota ZeroGPU).
7. **Intégration à Hyrule complet préparée, non lancée** : le même manifeste, planifié à blanc sur la composition complète 96×78, place 1 château, 4 tours, 4 ponts, 272 arbres, 11 rochers **sans erreur ni saut**.

## Limites restantes (précises)
- **Limite du pipeline** : les objets sont des **assemblages paramétriques dessinés à la main**, non reconstruits depuis la référence ; sans vue latérale, sans gros plan, sans fichier 3D de la référence, leur silhouette ne peut pas égaler celle du MOC. Le château V17 est trop massif et trop clair ; le réseau de rivières, les chemins, les fleurs et les petites constructions de la référence ne sont pas reproduits.
- Positions : ± 1,5 plot ; tailles/hauteurs estimées.
- Solidité : nouveaux risques **locaux** (troncs porteurs de couronnes, cônes de tourelles, arbres exposés) ; 2 liens faibles de type pilier déjà présents en V16 ; chiffres numériques, aucune mesure physique.
- Un seul angle de comparaison commun (dessus) ; trois-quarts comparé à la photo jointe seulement.

## Verdict
- **Technique : PASS pour la zone** (hors Photos→3D BLOCKED).
- **Artistique : aucun GO accordé** ; l'amélioration est **immédiatement visible** (volumes, ponts, rivières absents en V16) mais **encore loin de la référence** ; décision à prendre sur vos yeux (`renders/compare_*`).
- **Généralisation à Hyrule complet : NO-GO provisoire** tant que vous n'avez pas validé la zone ; si vous validez, étapes proposées : (1) affiner le château (silhouette plus sombre et élancée, douve) et les rivières (2 plots, bleu-gris) en maximum 3 cycles, (2) planifier les ≈ 10 ponts et 8–10 tours/repères du reste de la carte, (3) reconstruire la carte entière (≈ 31 min par passe) et refaire la régression. Aucun gel, aucune fusion dans `main`, aucun achat.
