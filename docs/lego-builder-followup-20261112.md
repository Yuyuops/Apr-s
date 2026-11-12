# Revue du 2026-11-12 — Beagle V1 livré numériquement, validation utilisateur requise

## Vérifications réellement effectuées
Lecture GitHub de la branche `research/lego-builder-commercial-outputs-20261108`, des rapports V13/V17, du suivi, du nouveau dossier `product_v1_beagle`, du manifeste de livraison et de l'acceptation utilisateur. Consultation de la liste GitHub des branches, du run Actions 43127587008 et de ses jobs, ainsi que de l'inventaire des fichiers et artefacts. **Aucun Python moteur, slicer ou imprimante exécuté pendant cette revue**. Les SHA-256 cités sont issus des rapports/manifestes du dépôt et non recalculés ici.

Branche observée : `9c3a85751d26a78d976c9f6f6acb6790ea29b100`. Workflow [43127587008](https://github.com/Yuyuops/Apr-s/actions/runs/43127587008), terminé le 12/11/2026 01:09:57 UTC, conclusion **success** ; job `final-cards-and-prototypes`, y compris gate de non-régression des cartes, **success**. Ce workflow n'est **pas** une validation du kit Beagle.

## Étape 1 — Régressions : PASS documenté / BLOCKED nouveau rejeu complet
- Nouveau rapport Beagle V1 : 10 567 pièces, 64 lignes pièce/couleur, 554 étapes, 561 pages ; modèle SHA-256 rapporté `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`. Les rapports déclarent BOM exacte, zéro collision/déconnexion/îlot et tests de non-régression PASS.
- GitHub Actions : le run 43127587008 valide les cartes et leurs SHA, pas l'ensemble des scripts Beagle/Photos→3D.
- Les branches Maps, Sculptures/Brickify, Photos→3D et Builder unifié restent identifiées dans GitHub. Aucune nouvelle exécution indépendante des tests complets n'a été lancée ici.

## Étape 2 — Moteurs : PARTIAL / pas de changement
- Beagle V12.1 conservé ; nouveau packaging sans modification des moteurs. Aucun correctif non testé.
- Hyrule V17 : château paramétrique validé géométriquement, mais NO-GO artistique ; ne pas généraliser sans validation.
- Photos→3D : dernier blocage quota Hugging Face, sujet inédit non qualifié. Pas de PASS nouveau.
- Points à risque Beagle : 147 étapes d'emboîtement par dessous, étape 447, 47 % des liaisons à un tenon. La validation physique reste BLOCKED.

## Étape 3 — Exports : PASS numérique rapporté / BLOCKED Bambu et physique
- Kit numérique Beagle : `benchmark-results/lego-builder/product_v1_beagle/LEGO_Builder_Beagle_V1_Digital_Kit.zip`, 24 407 713 octets, 29 fichiers, SHA-256 déclaré `3b81c4ac2662aaf6ef207f71273a4e2004195be654e184928f78a2119f4f340f`. **Présence et taille vérifiées via l'inventaire GitHub**, contenu et empreinte non recalculés ici.
- Kit expérimental Beagle : `LEGO_Builder_Beagle_V1_EXPERIMENTAL_Print_Files.zip`, 12 065 140 octets, SHA-256 déclaré `7d153ccf158e2dfee75c0eb104e7e8e6b3557c51b80fbb69d5922522b84c8ed6`. Présence vérifiée.
- Hyrule/Paco : exports numériques V13, 9 et 8 modules respectivement, validation numérique historique ; aucune nouvelle qualification Bambu Studio.
- Temps/masses Beagle : 8,9 kg/258 h pour briques individuelles et ~113 h pour modules selon formules, **pas** des mesures slicer ni des coûts fiables.

## Blocage nécessitant une intervention humaine
- **GO utilisateur absent** : faire lire la notice et tester un montage indépendant ; 554 étapes, dont 147 par dessous. Utiliser `USER_ACCEPTANCE_TEST.md` et la fiche du kit.
- **GO commercial absent** : droits des modèles/images et licence Hunyuan3D à clarifier, disponibilité et prix des pièces (plaque 4×6 Dark Orange ×945), coûts réels et solidité physique.
- **Bambu Studio / imprimante** : ouvrir les 3MF, imprimer le coupon de tolérance et mesurer l'assemblage avant toute promesse de compatibilité.

## Décision
**PASS technique documenté du Beagle V1 ; BLOCKED utilisateur, commercial et physique.** Alerte justifiée par la nécessité d'un testeur humain et d'une vérification des droits. Ne pas fusionner dans `main`, ne rien acheter, ne pas modifier les baselines CI. Continuer les contrôles Hyrule/Paco en parallèle seulement si une exécution réelle et traçable est disponible.
