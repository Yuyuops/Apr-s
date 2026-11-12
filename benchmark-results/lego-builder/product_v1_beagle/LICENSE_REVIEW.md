# Product V1 Beagle — Revue des licences et des droits

**Ceci n'est pas un avis juridique.** Il recense ce qui a été vérifié, ce qui ne l'a pas été, et conclut sur ce qui bloque une commercialisation. **Verdict : le produit n'est pas déclaré commercialisable.**

| Élément | Rôle dans le produit | Ce qui a été vérifié (11-12 nov. 2026) | Statut |
|---|---|---|---|
| **Tencent Hunyuan3D-2mv** (modèle de reconstruction 3D) | a produit le GLB du Beagle à partir de 4 images (`beagle_hunyuan2mv_reponse.json` : Space `tencent/Hunyuan3D-2mv`, graine 1234) | Licence communautaire *Tencent Hunyuan 3D 2.0* lue sur le dépôt du modèle : le territoire exclut **l'Union européenne, le Royaume-Uni et la Corée du Sud** (« DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA » ; usage hors territoire « unlicensed and unauthorized ») ; Tencent « ne revendique aucun droit sur les sorties » ; mentions obligatoires en cas de redistribution du modèle ; seuil de 1 M d'utilisateurs actifs ; usage militaire interdit ; interdiction d'utiliser le modèle ou ses sorties pour améliorer d'autres modèles d'IA ; droit de Hong Kong | **BLOQUANT** : la génération a été faite hors de toute garantie de territoire pour un opérateur européen ; l'effet sur les droits d'usage commercial du Beagle dérivé est à faire trancher par un juriste |
| **Images de référence du Beagle** (8 vues, `01_inputs_prepared`) | entrée de la reconstruction | `CONTROLE_COHERENCE.md` : « rendus de LEGO, pas des photos » ; origine et droits **non documentés** dans le dépôt | **NON ÉTABLI** |
| **Bibliothèque LDraw** | géométrie et noms de pièces pour rendus, GLB, validation ; non copiée dans le kit | Verrouillage du projet : `gkjohnson/ldraw-parts-library` (LDraw du 30 janv. 2023), licence indiquée **CC BY 4.0** ; attribution à LDraw.org requise ; texte de licence de la bibliothèque non relu ici | mention fournie ; relire la licence avant diffusion |
| **Rebrickable** (instantané `rb.db` : couleurs, années, nombre de sets) | valide les paires pièce/couleur ; la BOM contient `rebrickable_sets_containing_pair` et années | Conditions d'usage et licence des données **non relues** pour une diffusion commerciale ; l'instantané n'est pas redistribué mais des valeurs dérivées le sont | **À VÉRIFIER** |
| **brickify** (hamnaanaa) | convertisseur voxel → briques du pipeline | MIT d après REPRODUCTION.md (le verrouillage renvoie au LICENSE amont, non relu) ; code non distribué dans le kit | OK (hors kit), à relire |
| Marque **LEGO®** | nom « LEGO Builder » et références à des pièces compatibles | le groupe LEGO ne parraine pas le produit (mention dans le kit) ; usage du mot dans un nom commercial **non examiné** | **À EXAMINER** |
| Outils de génération (Python, ReportLab, Pillow, three.js, Chromium) | génèrent le PDF et les rendus | licences permissives usuelles ; polices : uniquement Helvetica de base du PDF (aucune police embarquée) | OK |
| Dépôt `Yuyuops/Apr-s` | code du projet | **aucun fichier LICENSE** à la racine : droits sur la notice, la BOM et les scripts non déclarés | **À DÉCIDER par le propriétaire** |
| Pièces LEGO réelles | achat de pièces par le client | aucun achat ni vérification de stock ici ; couleur Dark Orange (484) = 6 263 pièces | non vérifié |

## Conséquences
- **GO commercial impossible aujourd'hui** : (1) licence du modèle de génération vs territoire UE, (2) droits sur les images de référence non établis, (3) conditions Rebrickable, (4) licence du dépôt, (5) usage de la marque non examinés.
- Distribution **privée de test** (équipe projet) : raisonnable ; les mentions LDraw/Rebrickable/LEGO sont dans `LICENSES/LICENSES.md` du kit.
