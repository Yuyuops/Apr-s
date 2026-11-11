# Revue du 2026-11-11 — contrôle GitHub et qualification des preuves

## Périmètre réellement exécuté
Lecture via connecteur GitHub des documents `docs/lego-builder-execution-status.md`, `docs/lego-builder-product-direction-20261108.md`, `sprint_v16_closure/REGRESSION_FINAL.md`, `sprint_v17/FINAL_VERDICT.md` et `sprint_v13/BAMBU_READINESS.md`. Recherche des branches `research/lego-maps-*`, `research/lego-brickify-benchmark`, `research/lego-builder-photos-to-lego` et `research/lego-builder-unified`. Les README des deux branches historiques Photos et Brickify pointent vers l'ancien projet Après : **ne pas les interpréter comme preuves LEGO**. Aucun moteur, CI, slicer ou imprimante exécuté pendant cette revue. Aucune empreinte d'artefact recalculée.

## Étape 1 — Non-régression : PASS historique / BLOCKED nouveau rejeu
- Rapport de clôture V16 (commit f962b6a) : 8/8 baselines Maps IDENTICAL ; unitaires 9/9 ; moteur V16 2/2 ; Italie, Paco, Beagle IDENTICAL ; Photos→3D Paco PASS au moment du test.
- Empreintes SHA-256 **rapportées et non recalculées aujourd'hui** : Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`, Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`.
- Rapport V17 : baselines et tests objets PASS rapportés ; Photos→3D BLOCKED quota ZeroGPU ; validation d'un sujet inédit toujours absente.
- Limite de la revue : le connecteur utilisé permet de lire les fichiers GitHub mais n'expose pas ici de lancement arbitraire des tests Python ou d'un nouveau workflow. Statut de **rejeu ce jour : BLOCKED**, pas PASS.

## Étape 2 — Moteurs : PARTIAL / gel NO-GO
- Maps V17 : zone château de 1 950 pièces, 0 collision / déconnexion / îlot / non-supportée, mais fidélité artistique insuffisante ; château trop massif, chemins et rivières à revoir ; 81 pièces porteuses à un tenon, sans essai physique.
- Sculptures Paco/Beagle : empreintes historiques conservées ; pas de nouveau correctif ni de rendu aujourd'hui.
- Photos→3D : quota externe persistant dans le dernier rapport, disponibilité actuelle non testée ; généralisation non prouvée.
- Builder unifié : régression historique documentée, aucune nouvelle exécution.
- **Aucune correction moteur appliquée aujourd'hui** : un changement non testé serait contraire à la règle de préservation des baselines.

## Étape 3 — Export Bambu : PARTIAL numérique / BLOCKED natif et physique
- V13 : STL/3MF Hyrule/Paco numériques existants, 9 modules Hyrule et 8 modules Paco, contrôle de volumes/étanchéité documenté ; connecteur de tenon ajouté ; PrusaSlicer 2.7.2 utilisé comme proxy.
- Défauts/risques documentés : approximation de certaines formes, ponts de tuiles, affectation couleurs non vérifiée dans Bambu Studio, aucun coupon imprimé ni tolérance mesurée.
- Temps et coûts V14 : estimations par profils proxy, **pas** des mesures Bambu ; BOM/notice et tarifs à revalider avant décision commerciale.
- **Aucun nouvel STL/3MF, tranchage, BOM ou notice produit aujourd'hui.**

## Décision et prochaine exécution
1. Obtenir un runner capable de récupérer la branche et de rejouer les scripts de régression, avec logs, code de sortie, SHA des entrées/sorties et commit exact ; ne pas confondre rapport historique et nouvelle exécution.
2. Ne corriger que des défauts reproduits sur ce runner, avec tests et rendus avant/après ; conserver les options expérimentales désactivées par défaut.
3. Qualifier les exports existants dans Bambu Studio et réaliser le coupon physique avant tout GO fabrication. Tant que Bambu Studio et une imprimante ne sont pas accessibles, conserver **BLOCKED physique**.
4. Hyrule : pas de gel artistique sans comparaison humaine de la zone château ; ne pas lancer le modèle complet.

Aucun achat, aucune fusion main, aucun changement de référence CI. Cette revue ne constitue **ni** une livraison de trois étapes validées **ni** un GO commercial.
