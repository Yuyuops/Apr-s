# Sprint V15 — Audit de la détection du besoin / interprétation de la demande

Méthode : lecture du code (`lego_builder/*.py`, `cli.py`, schéma du manifeste, `data/`), recherche textuelle dans les documents, puis **exécution réelle** sur l'image de référence de Hyrule. Rien n'est tenu pour acquis parce qu'un document le mentionne.

## 1. Inventaire (état au début du sprint)
| Composant | Existe dans le code ? | Opérationnel ? | Preuve |
|---|---|---|---|
| **Classification du type de modèle** (`analyze.py`) : carte / sculpture / mosaïque / indéterminé, par statistiques de couleur (eau, végétation, neige, sable), uniformité de la bordure, canal alpha, cadre sombre | oui | **oui**, heuristique, listes de preuves et d'incertitudes | `python -m lego_builder analyze` sur la référence : `map_relief_25d`, confiance 0,95 ; tests unitaires |
| **Choix automatique du générateur** (`GEN`, `cli.prepare`) | oui (table de 4 entrées) | oui pour carte, GLB, photos ; mosaïque → `needs_input` | `cli.py` l. 11–12, `prepare()` |
| **Surcharge manuelle du type** (`--type`) | oui | oui | `cli.py` |
| **Manifeste de projet strict** (SHA-256 des sources, statut, incertitudes) | oui | oui | `manifest.py`, `schema/project_manifest.schema.json`, `test_unit.py` |
| **Préparation d'une carte depuis image** (`map_ingest.py` : détection du plateau, rectification, classes par règles HSV) | oui | **opérationnel mais peu fiable sur cette référence** (voir §2) | exécuté |
| **Orchestration des 3 moteurs** (Maps, Sculpture, Photos→3D) | oui (`core.py`, `generators/`, `reconstruct.py`) | oui | CI « LEGO Builder regression » |
| Générateur **Mosaïque/2D** | **non** : refus explicite (`needs_input`) | — | `cli.py`, `GENERATOR_INTERFACES.md` |
| **Interprétation d'une demande en langage naturel** | **non** | — | aucune fonction ne lit un texte de demande ; seul `--title` existe |
| **Extraction de contraintes** (dimensions, régions à préserver, repères, palette souhaitée, niveau de détail) | **non** : le manifeste n'a que `target.size_mm` et des `parameters` libres | — | `project_manifest.schema.json` |
| **Analyse sémantique d'image** (reconnaître régions, objets, version d'un sujet) | **non** | — | `analyze.py` ne fait que des statistiques de couleur |
| **Détection de la version d'un sujet** (plusieurs Hyrule) | **non** | — | aucune trace |
| **Planification de construction** | **non** (le Builder enchaîne des étapes figées) | — | `cli.py` |
| Référence documentaire à une « détection du besoin » | seulement `IMAGE_INGESTION.md` (analyse de nature/type, sans interprétation de la demande) | — | recherche textuelle : aucun document n'annonce un module d'intention |

**Conclusion honnête** : la « détection du besoin » qui existait réellement se réduit à **un classifieur de type heuristique** (`analyze.py`) plus un routage par table. Il n'y a **ni interprétation de la demande, ni extraction de contraintes, ni sémantique d'image, ni détection de version** : ils n'ont jamais été implémentés (ce n'est pas « configuré mais non raccordé » : il n'y a rien à raccorder).

## 2. Test réel sur la référence de Hyrule
- `analyze` : carte 2,5D, confiance 0,95, cadre sombre détecté → **le routage vers LEGO Maps est correct**, mais il ne dit ni quel Hyrule, ni quelles régions, ni les proportions.
- `prepare --type auto` (chemin automatique `map_ingest`) : statut `ready_for_generation`, **mais** les coins détectés `[[88.6,76],[1150.5,44.6],[1152.4,966.2],[47.9,966.2]]` forment un trapèze (vrai rectangle de carte mesuré : x 40→1168, y 56→972) et la distribution de classes (`eau 21 %, herbe 28 %, roche 12,7 %, …`) ne distingue ni hors-carte, ni lacs, ni cratère. Le chemin automatique n'est donc **pas suffisant** pour piloter un rendu fidèle ; il est conservé tel quel (pas de refonte).
- V14 (Hyrule généré par un fichier de règles HSV écrit à la main sur l'image fournie à l'époque, SHA 4b9c7b22…) : proportions supposées carrées (rapport 1,0 au lieu de 1,231).

## 3. Ce qui manquait pour l'utiliser sur Hyrule, et ce qui a été ajouté (composant minimal, sans refonte)
| Manque | Ajout V15 |
|---|---|
| Canal fiable pour ce qu'une image ne dit pas (sujet, version, régions, rectangle de carte, proportions) | **manifeste d'exigences structuré** (`HYRULE_REQUIREMENTS.json`, validé par `intent.validate_requirements`) rempli par l'opérateur ; **aucune compréhension d'image n'est simulée** |
| Interprétation de la demande et routage | `lego_builder/intent.py` + commande `python -m lego_builder intent` : combine (1) exigences structurées, (2) mots-clés FR/EN du texte de la demande, (3) `analyze` ; renvoie type, générateur, preuves, **blocages et questions** ; hors ligne, sans API payante |
| Version d'un sujet ambigu | `data/subject_versions.json` : tout sujet connu en plusieurs versions (Hyrule, Terre du Milieu, Westeros) **bloque** (`needs_input`) tant qu'aucune version n'est choisie |
| Préparation sémantique d'une carte | `lego_builder/semantic_map.py` : classification par prototypes Lab (mesurés sur la référence, nommés par l'opérateur), règles de connectivité (hors-carte / cratère), bandes d'altitude ; entièrement données-pilotées |
| Tests | 3 tests unitaires (routage des 4 types, refus de version ambiguë, validation des exigences) — 9/9 verts |

## 4. Preuves de fonctionnement (`intent_plans/*.json`)
| Entrée | Statut | Type → générateur | Remarque |
|---|---|---|---|
| Hyrule + exigences (version BotW) + image | **ready** | carte → `maps` | décidé par les exigences structurées |
| Hyrule + exigences **sans version** | **needs_input** | carte → `maps` | « sujet existant en plusieurs versions : aucune choisie » |
| « carte de Hyrule » + image, sans exigences | **needs_input** | carte → `maps` | version non fournie → refus (pas de deviner) |
| « sculpture de mon chien à partir de quatre photos » + 4 images Paco | ready | photos → `photos_to_3d` | |
| « un logo en mosaïque » | needs_input | mosaïque → `mosaic` | générateur non implémenté : refusé, pas simulé |
| « fais-moi quelque chose de joli » | needs_input | indéterminé | pose la question du type |

## 5. Limites restantes
- La lecture sémantique d'une image (reconnaître que c'est BotW, nommer les régions) reste **manuelle** (exigences structurées) : aucun modèle de vision n'est disponible hors API payante.
- Les mots-clés sont simples (français/anglais) ; une demande atypique tombe en `undetermined` et pose une question.
- Le routage Sculpture/Photos s'appuie sur le nombre d'images ; la reconnaissance de vues reste dans `reconstruct.find_views`.
- Aucun gain de **rendu** n'est attribuable au routage seul (le type « carte » était déjà détecté) : le gain mesuré vient du **manifeste (proportions, zone, classes)** — voir `PIPELINE_COMPARISON.md`.
