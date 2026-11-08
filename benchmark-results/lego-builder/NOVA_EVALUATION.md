# Évaluation de LDraw Nova comme validateur indépendant
Dépôt examiné : `anteloc/ldraw-nova` (commit `cdf95d6b`, clone superficiel), installé dans un environnement séparé (`pyldraw3 1.7.0`, `numpy`, `jsonschema`, `ldraw-xray 0.1.0`). Nova n'est **pas** importé par le builder : `tools/nova_check.py` et `tools/nova_components.py` le lancent à part.

## Ce que c'est
Outils Python de génération et de revue de modèles LDraw pilotés par un agent (CLI `ldraw-agent`, interface web Docker). Modules utiles : `validation.py` (syntaxe et structure LDraw), `geometry.py` (`analyze_geometry` : recouvrements de corps rectangulaires par test d'axes séparateurs, couverture de connecteurs, composantes connexes), `connectivity.py`, `collision.py`. Autres parties hors sujet : génération par LLM, recherche sémantique (clé TypeSafe facultative), rendu LeoCAD, VR.

## Licence (à faire relire par un juriste)
Code : **AGPL-3.0**. Documentation : CC BY-SA 4.0. Dépendances : `pyldraw3`, `ldraw-xray` (licences non auditées ici). Conséquences pratiques : utiliser Nova comme **outil séparé** (processus distinct, non distribué avec nos produits) pour contrôler nos modèles n'oblige pas à ouvrir notre code ; l'intégrer dans un service en réseau ou le redistribuer déclencherait les obligations de l'AGPL sur l'ensemble combiné. **Décision : pas d'import, pas de copie de code.**

## Test comparatif (mêmes modèles)
| Modèle | Pièces | Nos contrôles | Nova (diagnostics LDraw) | Nova (recouvrement de corps) | Nova (connexion, mode optimiste) | Durée Nova |
|---|---:|---|---|---|---|---:|
| Paco V12.1 | 3 193 | 0 collision, 0 déconnectée | 0 erreur (1 avertissement de fin de ligne) | 0 | **6 composantes : 1 + 5 pièces isolées** | 36 s |
| Beagle V12.1 | 10 567 | 0 collision, 0 déconnectée | idem | 0 | **3 composantes : 1 + 2 isolées** | 183 s |
| Hyrule biomes | 10 682 | 0 collision, 0 déconnectée | idem | 0 | **1 composante** | 212 s |
| Italie | 13 633 | 0 collision, 0 déconnectée | idem | 0 | non mesuré (diagnostics seuls : 0 erreur) | 120 s |
Le mode « connecté confirmé » de Nova donne des milliers de composantes sur nos modèles : il ne confirme que les contacts dont il connaît le connecteur (tuiles, plaques empilées…) ; ce chiffre **ne signale pas** de défaut réel.

## Ce que Nova trouve en plus
Pièces sans contact même en mode optimiste : Paco 5 (`43898` coupole 3×3 inversée ×3 et `98138` tuile ronde 1×1 ×2 : les yeux et la truffe), Beagle 2 (`3960` coupole 4×4 inversée, `6141` plaque ronde). Notre graphe les relie par des tenons (fixation SNOT sur `87087`). **Constat non tranché** : soit une lacune des métadonnées de connexion de Nova pour les coupoles inversées (hypothèse la plus probable : toutes les pièces concernées sont des coupoles ou leurs pupilles), soit un vrai défaut de fixation. **À vérifier physiquement** ; aucun modèle accepté n'a été modifié.

## Décision
Gain mesurable : **faible** (aucun défaut structurel confirmé de plus ; un signal inconclusif sur 7 pièces de détail). Coût : AGPL, dépendances externes, 36 s à 3 min par modèle. **Ne pas ajouter la dépendance.** Conserver les deux scripts comme contrôle croisé facultatif, à relancer si les modèles changent. Intégration ciblée envisageable seulement si l'on trouve un cas où Nova détecte un défaut confirmé.

## Brickalike
Introuvable : une recherche web ne renvoie aucune page ni dépôt portant ce nom. **BLOCKED** : aucune licence, aucune géométrie examinée, rien réutilisé. D'autres générateurs de briques imprimables apparaissent (MachineBlocks, PrintPal, FreeCAD-Brick), sans licence vérifiée : **non utilisés**. La géométrie d'impression du builder est entièrement paramétrique et écrite pour ce projet.
