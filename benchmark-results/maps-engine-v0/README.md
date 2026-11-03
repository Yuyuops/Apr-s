# LEGO Maps — Moteur 2 / V0

**État : paquet d'entrées et mission; aucun moteur 2 n'est encore développé.**

Branche dédiée : `research/lego-maps-v0-20261103` issue du moteur 1 V12.1 (commit `dca6993`). Ne pas fusionner dans `main`.

But : conversion d'une image de carte en tableau LEGO **2D ou relief 2.5D**, avec contours, couleurs, fond rigide, LDraw, rendu, nomenclature et notice. Pas de GLB ni de reconstruction volumique.

Entrée : `fixtures/ile_temoin.svg`, **carte fictive originale**. Test de 32×32 tenons (25,6 × 25,6 cm). Relief à hauteurs artistiques de 0 à 4 plates, pas des altitudes réelles.

`fixtures/ile_temoin_oracle.json` donne les couches **réservées à l'évaluation**. Le moteur doit inférer depuis l'image, pas lire l'oracle. `scripts/make_fixture.py` permet de produire une entrée PNG et une heightmap de contrôle, avec Pillow.

`fixtures/map_config.json` spécifie le test; `MISSION_V0.md` décrit les étapes et critères. Réutiliser les outils techniques de `../20_portable_engine/` sans modifier le moteur 1.

IMPORTANT : pour tarifs et stock des pièces, vérifier **Briquestore uniquement**. Aucun tarif ou stock n'est fourni dans ces fichiers; laisser inconnu quand non vérifié. Aucun achat, déploiement, copie d'une carte protégée ni validation physique prétendue.
