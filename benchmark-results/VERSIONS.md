# Versions et provenance (figées le 2026-10-31)

| Élément | Source | Version / SHA |
|---|---|---|
| brickify (original, non modifié) | https://github.com/hamnaanaa/brickify | `1564bb3b2704c522e084fdb1b2a3ce9d3f11d300` |
| AutoTile | https://github.com/7kzaincode/autotile | `bf16473597a26924ec89909723e11a581e125973` |
| Bibliothèque LDraw officielle | miroir GitHub https://github.com/gkjohnson/ldraw-parts-library (library.ldraw.org est bloqué par le réseau de la session) | `1f24cac1821b9a86a5a84cd3a40291aad24679b3`, LDConfig « UPDATE 2022-03-31 », bibliothèque téléchargée le 2023-01-30 |
| Catalogue Rebrickable (existence pièce×couleur, n° d'élément) | https://github.com/ojuuji/rb.db release latest-v8 | data_timestamp 1793454908 (oct. 2026) |
| Proxy de répétition | KhronosGroup glTF-Sample-Assets, Models/Fox (CC-BY 4.0 / CC0) | `8f492390ddc7a2ae221a1369ef560589cf8c70fb` |
| Python | venv | Python 3.13.18 ; trimesh 5.2.0, numpy 2.5.4, scipy 1.18.1, networkx 3.7 |
| Rendu | three.js 0.160.0 (npm), Chromium/Playwright préinstallé, WebGL SwiftShader | Node v22.23.4 |
| Modèle photo→3D | Hunyuan3D-2mv, démo Hugging Face officielle `tencent/Hunyuan3D-2mv` (gratuite, ZeroGPU), modèle `hunyuan3d-dit-v2-mv-turbo`, forme seule | Space commit `98b78666ba43239564d6607fd0d45d9b43581fdc` ; gradio_client 2.7.2 |
| Couleurs du GLB | projection des 4 images de référence (`tools/colorize_from_views.py`), visibilité par lancer de rayons | embreex 4.4.0.post1, Pillow 13.0.0 |
| fal.ai Hunyuan3D v3.1 Pro | **non exécuté** (prix officiel relu : 0,375 $ + 0,15 $ multivue = 0,525 $ par génération) | — |
| AutoTile (dépendances chemin `--mesh`) | venv commun | scikit-learn 1.9.1, rtree 1.4.1 |
