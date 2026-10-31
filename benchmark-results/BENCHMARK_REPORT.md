# Benchmark des moteurs de construction LEGO : rapport intermédiaire

**Statut au 2026-10-31 : BLOQUÉ.** Les deux chiens (Paco, Beagle) n'ont pas encore été traités.
Trois éléments extérieurs à la session manquent (voir §1). Toute la chaîne en aval est prête et a été testée
de bout en bout sur un proxy libre de droits, un renard texturé (Khronos *Fox*, CC-BY 4.0).
**Ce proxy n'est pas un des chiens et ne sert pas à juger le moteur sur vos sujets.**

Aucune décision GARDER / AMÉLIORER / ABANDONNER n'est encore prise : elle demande les rendus des vrais chiens.

---

## 1. Blocages qui demandent votre intervention

| # | Blocage | Constat | Ce qu'il faut faire |
|---|---|---|---|
| 1 | ~~`brickify_test_integral.zip` introuvable~~ **RÉSOLU** | Le zip a été reçu. 8 vues ont été détourées et contrôlées : voir `01_inputs_prepared/CONTROLE_COHERENCE.md`. | — |
| 2 | `FAL_KEY` absente | Variable non définie dans l'environnement. Sa valeur n'a jamais été affichée. | Créer une clé sur https://fal.ai/dashboard/keys, puis l'ajouter comme variable d'environnement `FAL_KEY` dans les paramètres de l'environnement cloud (menu de l'environnement dans la barre de titre de la session → Edit → Environment variables). Démarrer ensuite une nouvelle session, ou me dire de relancer. |
| 3 | Réseau : fal.ai bloqué | `fal.ai`, `queue.fal.run` et `rest.alpha.fal.ai` ne résolvent pas. Le CDN de sortie (`*.fal.media`) est sans doute bloqué aussi. | Paramètres de l'environnement → Network access : ajouter `fal.ai`, `queue.fal.run`, `rest.alpha.fal.ai`, `fal.media`, `v3.fal.media` et `v3b.fal.media` aux domaines autorisés, en laissant cochée la case « Allow package managers ». Doc : https://code.claude.com/docs/en/cloud-environments#network-access |
| 4 | Prix à confirmer avant tout appel payant | Impossible de lire la page tarifaire de fal.ai (domaine bloqué). Seules des sources tierces sont disponibles : fal `hunyuan3d-v3/image-to-3d` à **0,375 $ par génération** d'après costgoat.com et d'après le docstring de `image_to_3d.py` (« Sept 2026 »). | Une fois le réseau ouvert, je relis le prix officiel et le schéma de l'API (paramètres multivues, existence d'une v3.1 Pro), puis je vous demande votre accord avant d'exécuter. |

Également bloqués, mais contournés : `library.ldraw.org` (remplacé par le miroir GitHub de la bibliothèque officielle),
ainsi que `rebrickable.com` et `bricklink.com` (remplacés par la base Rebrickable publiée sur GitHub par ojuuji/rb.db).
BrickLink Studio n'est pas disponible : c'est une application Windows/macOS sans version Linux ni mode ligne de commande.

## 2. Ce qui est prêt et vérifié

Les scripts sont dans `tools/`, les versions et SHA dans `VERSIONS.md`.

| Étape | Outil | Vérifié sur |
|---|---|---|
| Moteur | `brickify/pipeline/brickify.py`, dépôt original, **non modifié** (SHA `1564bb3`) | proxy Fox |
| Rendus LEGO | `ldr_expand.py` + `render_ldr.js` : chaque triangle provient des fichiers `.dat` de la bibliothèque LDraw officielle référencés par le `.ldr`. Rendu three.js WebGL, sans retouche ni IA générative. Six vues : face, profil gauche, 3/4 avant, arrière, dessus, éclatée. | exemple Muse du dépôt, proxy Fox |
| Rendus du GLB | `render_glb.sh` : 4 vues, mise à l'échelle 250 mm | proxy Fox |
| Validation indépendante | `validate_ldr.py` : n'utilise pas les contrôles de brickify. Collisions par occupation, graphe des connexions par tenon, pièces déconnectées, pièces posées dans le vide selon l'ordre de la notice, points de rupture uniques (ponts du graphe), appuis des sous-ensembles (oreilles, tête), porte-à-faux horizontaux (queue, museau), pieds, centre de masse et angle de basculement, existence de chaque couple pièce × couleur dans Rebrickable. | proxy Fox |
| Notice | `make_instructions.py` : PDF d'une page par couche, couches précédentes en pâle et liste des pièces à poser | proxy Fox (77 pages) |
| Planche comparative | `make_board.py` : recadrage et mise à l'échelle seulement | proxy Fox |
| Chaîne complète | `run_model.sh <glb> <nom> <dossier> [args brickify]` | proxy Fox |

## 3. Constats sur brickify, d'après le code et la répétition sur le proxy

Ces constats ne dépendent pas des chiens. Ils seront revérifiés sur Paco et le Beagle.

1. **`--components` vaut 1 par défaut.** Seul le plus grand composant connexe du maillage est conservé
   (`load_and_voxelize`). Une oreille, une queue ou une patte modélisée comme une coque séparée est donc **supprimée sans avertissement**.
   Il faudra compter les composants de chaque GLB avant la conversion et passer `--components N` si nécessaire.
2. **Le catalogue de pièces ignore les couleurs.** brickify place n'importe quelle taille de pièce dans n'importe quelle couleur.
   Sur le proxy, **102 briques 2×8 (3007) et 32 briques 1×8 (3008) en Bright Light Orange n'ont jamais été produites**
   selon Rebrickable. Le modèle n'est donc pas constructible tel quel. Le critère « toutes les pièces existent réellement » échoue.
3. **« Vérification des collisions » : il n'existe pas de contrôle séparé.** L'absence de chevauchement découle de la construction
   (une grille d'occupation). Mon contrôle indépendant confirme 0 collision sur le proxy.
4. **La connectivité est vérifiée, l'ordre de montage ne l'est pas.** 0 pièce déconnectée sur le proxy, mais
   **193 pièces sur 1 805 n'ont rien sous elles au moment où la notice les fait poser**. Elles ne tiennent que par des pièces placées plus haut,
   dans une étape ultérieure. L'espace sous elles est libre, donc elles peuvent probablement être emboîtées par en dessous plus tard,
   mais la notice générée est fausse sur ces étapes.
5. **Faiblesses mécaniques détectées sur le proxy (indices géométriques, pas un essai physique) :**
   - la queue (15,7 % de la masse) ne tient au corps que par **5 pièces réparties sur 2 couches** au plan de raccord ;
   - 1 582 des 2 593 liaisons sont à **un seul tenon** ;
   - 561 points de rupture uniques (une seule liaison retient un sous-ensemble) ;
   - le corps entier repose sur 19 tenons au niveau des pattes ;
   - les oreilles tiennent par 6 à 12 tenons ;
   - le centre de masse est dans le polygone d'appui, avec 32,6 mm de marge (basculement à environ 13°).
6. **La sortie est probablement l'image miroir du maillage.** brickify inverse Y et garde X et Z (`write_ldraw`), alors que
   LDraw et glTF sont tous deux des repères directs. L'effet est invisible sur un sujet symétrique, mais une marque asymétrique
   (tache sur un flanc, oreille relevée d'un seul côté) changera de côté. À contrôler visuellement sur le Beagle.
7. **Les couleurs sont tirées d'une palette de 37 teintes au plus proche.** Avec le `--gain 1.3` du README, l'orange du renard devient
   « Bright Light Orange ». C'est un réglage d'art direction qui modifie fortement la fidélité.
8. **Le rendu reste « cubique ».** Le catalogue ne contient que des briques et des plaques rectangulaires
   (pas de pentes, tuiles ni pièces arrondies), et le pas de voxel horizontal est de 8 mm. Sur le proxy à 250 mm,
   la silhouette est reconnaissable, mais les oreilles se réduisent à des colonnes de 1×1 et le museau à des marches.
   C'est structurel : le moteur ne propose aucun réglage pour changer cela.

## 4. Suite prévue dès le déblocage

1. Décompresser le zip dans un dossier isolé, lire les instructions complémentaires, contrôler la cohérence face / profil / arrière, détourer les sujets.
2. Relire la documentation et le prix officiels de fal.ai, choisir le meilleur modèle multivue réellement disponible, puis **vous demander votre accord sur le coût**.
3. Générer le GLB de chaque chien, avec 4 vues, ses dimensions et une évaluation de fidélité. Signaler tout maillage incorrect avant la conversion.
4. Lancer brickify : d'abord un passage brut avec les paramètres documentés à 250 mm, conservé tel quel. Ensuite des réglages documentés
   (`--components`, `--gain`, `--exclude`, `--interior`, `--palette-*`) et un essai à 400 mm.
5. Produire les rendus et la validation, la notice, les fichiers `paco_reference_vs_lego.png` et `beagle_reference_vs_lego.png`,
   puis lancer la comparaison AutoTile sur les mêmes GLB si brickify échoue. Écrire enfin le tableau de décision.

Coût des pièces : **coût non vérifié** (aucune donnée de marché accessible depuis la session).
