# MISSION — LEGO Maps V0, premier tableau en relief

Dépôt : `Yuyuops/Apr-s`, branche `research/lego-maps-v0-20261103`.
Dossier : `benchmark-results/maps-engine-v0/`.
Référence moteur 1 : `../20_portable_engine/`.

**Objectif :** transformer `fixtures/ile_temoin.svg` (ou son PNG produit par `scripts/make_fixture.py`) en tableau LEGO 2.5D de **32×32 tenons, 256×256 mm**, constructible numériquement. Ce n'est ni une sculpture 3D ni une conversion GLB.

1. Vérifier l'entrée, les dépendances LDraw et les modules réutilisables du moteur 1 : catalogue géométrique, validation collisions/liaisons, rendu et notice. Moteur 1 strictement en lecture seule, conserver Paco option A et Beagle V12.1.
2. Archiver **un premier essai aveugle** à partir de l'image seule, avant tout ajustement. `fixtures/ile_temoin_oracle.json` n'est autorisé qu'**après** ce premier essai, pour évaluer les résultats.
3. Implémenter le flux générique `image SVG/PNG/JPG → grille 32×32 → classes/couleurs → niveaux de hauteur → pavage LEGO → fond structurel → validations → exports`. Le relief est **artistique** et les hauteurs proviennent d'une convention de style déclarée, jamais d'altitudes géographiques inventées.
4. Classer eau, terre, forêt, colline, sommet, route, rivière et village. Respecter les frontières fines, limites de terre et détails importants. Représenter les hauteurs par plaques de 3,2 mm; choisir des couleurs LEGO selon la proximité colorimétrique avec la source.
5. Optimiser le pavage (1×1, 1×2, 1×3, 2×2, 2×4 et autres dimensions **réellement existantes**) en arbitrant fidélité des contours, nombre de pièces, connexion et accessibilité. Éviter les milliers de 1×1 par défaut; comparer une sortie 2D sans relief à la sortie 2.5D.
6. Produire un dos rigide par assemblage décalé, des connexions réelles entre zones et des niveaux sans éléments flottants. Vérifier zéro collision, zéro déconnexion, les joints, la stabilité numérique et les dimensions. Aucun dispositif mural déclaré sûr sans essai réel.
7. Produire un modèle LDraw `map.ldr`, une nomenclature `parts_list.csv` avec référence/couleur/quantité, un aperçu HTML zoomable, des rendus face/profil/trois-quarts et une notice PDF **par régions et couches**, avec pièces traçables. Ne pas simuler les sorties : un fichier manquant doit être signalé.
8. Pour prix et stocks, **Briquestore seul** (https://store.bricklink.com/briquestore.fr ou catalogue officiel) : valeur et date de vérification ou `null` si inconnues; ne pas prétendre une commande réalisable sans quantité stock confirmée. LDraw/Rebrickable servent aux propriétés techniques, pas à la vérité du stock d'un vendeur. Pas de contournement d'accès.
9. Évaluer après le premier essai avec l'oracle : IoU par classe, fidélité des frontières, erreur des couleurs des vraies pièces, pourcentage de 1×1, nombre de pièces, liaisons, défauts, régions, étapes, coût seulement si réellement vérifié. Faire un deuxième test simple, image différente et non codée en dur.

**Livrables** : `results/essai1/`, `results/map.ldr`, `results/parts_list.csv`, `results/viewer.html`, `results/notice.pdf`, `results/renders/`, `results/validation/`, `results/RAPPORT_V0.md`, `results/VERDICT.md`.

Verdict : **V0 VALIDÉ** si image→LEGO→rendu/LDraw/BOM/notice complet, cohérent et vérifié numériquement; **V0 AVEC LIMITATIONS** si une limite mesurée persiste; **À CORRIGER** en cas d'échec de génération, d'assemblage ou de données inventées.

Aucun achat, aucun déploiement, aucune fusion dans `main`, aucun moteur 2 présenté comme terminé avant tests, aucune modification du moteur 1, des GLB ou des archives.
