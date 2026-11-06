# Interfaces des générateurs
Contrat : un générateur reçoit un projet **prêt** (manifeste `ready_for_generation`) et écrit dans `model/` : `diorama.ldr`, `parts_list.csv`, ses validations ; il renvoie un résumé stocké dans `manifest.results`. L'orchestrateur appelle ensuite le cœur (catalogue, validations, rendus).

## Générateur 1 : cartes et reliefs 2,5D (`generators/maps.py`)
Entrée : `composition.json` + `style.json` (+ classes de terrain en TIFF pour le mode biomes). **Les modes côte/mer et biomes/relief sont deux variantes du même générateur** (`build_style.py`) : la composition donne soit une fenêtre géographique, soit une carte de classes ; le style donne la palette, le relief, le cadre, le titre. Sortie : LDraw, nomenclature, métriques, fragilité, plan par couches, rendus, `delivery_check.json` (concordance LDraw / nomenclature / plan).
Réutilisé tel quel : LEGO Maps V1.0. Ajouts de cette mission : correction générique d'un défaut (filets de cadre de longueur impaire) et titre sur terre, sans changer aucun modèle existant (LDraw identiques).

## Générateur 2 : sculptures 3D (`generators/sculpture.py`)
Entrée : GLB + configuration de sujet. Sortie : LDraw, nomenclature (`parts_list.csv` issu du catalogue), validations du moteur 1, plan de montage hiérarchique, rendus comparés au GLB de référence. Réutilisé tel quel : `lego_run.py` (de la lecture du GLB à la notice), `render_compare.py`. Aucune modification du moteur 1.
Limites : segmentation propre à Paco (bipède) et au Beagle (quadrupède) ; pour un GLB inconnu la configuration est générique et **non validée**.

## Générateur 3 : mosaïques et tableaux 2D
**Non réalisé.** Décision : la consigne limitait cette famille à un adaptateur minimal « s'il peut réutiliser le pavage existant ». Le pavage des cartes travaille sur des niveaux avec appuis ; une mosaïque plane en plaques est un cas dégénéré mais demande une quantification de couleurs et un choix de pièces (tuiles, plaques) que je n'ai pas validés. L'orchestrateur reconnaît le type et répond explicitement « non implémenté » (statut `needs_input`). Je n'ai pas lancé ce chantier avant d'avoir stabilisé les deux premières familles.

## Orchestrateur (`cli.py`)
`analyze` → `prepare` (copie la source, analyse, convertit, écrit le manifeste) → `build` (générateur, cœur, résultats) ; `run` enchaîne ; `geo` lance le mode côte/mer sur une composition géographique ; `check` valide le manifeste. Ligne de commande seulement : **aucune interface web n'a été construite**.
