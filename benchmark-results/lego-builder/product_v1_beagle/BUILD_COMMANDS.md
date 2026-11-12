# Product V1 Beagle — Commandes de reproduction

Environnement : `LEGO_ENGINE_HOME` = dossier du moteur portable installé (`20_portable_engine`, dépendances installées par `scripts/install.sh`), Python 3.13, Node 22, reportlab (système).
```
# 1. modèle + plan de notice (reproductible : SHA-256 551bde0f…)
python -m lego_builder run 02_glb_gratuit_hunyuan2mv/beagle.glb --out RUN --size-mm 400 --notice full
# 2. rendus d'étapes du moteur (images, ~85 min sur 4 cœurs sans GPU)
python 20_portable_engine/engine/make_notice_pdf.py RUN/model/run/notice/beagle_plan.json RUN/model/run/notice/beagle_notice.ldr RUN/model/run/notice/beagle_map.json OUT beagle      # produit OUT/r/sNNN.png
# 3. rendus haute résolution + GLB + tour animé
python lego-builder/tools/product_renders_v1.py 22_color_structural_regression/modeles/beagle_V121/beagle_brut.ldr RENDERS
# 4. BOM
python lego-builder/tools/product_bom_v1.py MODEL.ldr CATALOGUE.csv NOMENCLATURE.csv BOMDIR
# 5. notice PDF
python lego-builder/tools/product_notice_v1.py PLAN MAP NOTICE.ldr OUT/r CATALOGUE.csv rb.db RENDERS Beagle_V1_Notice.pdf steps.csv notice_report.json --sha SHA
# 6. kit + validation
python lego-builder/tools/build_kit_beagle_v1.py KITDIR LEGO_Builder_Beagle_V1_Digital_Kit.zip
python lego-builder/tools/validate_product_v1.py LEGO_Builder_Beagle_V1_Digital_Kit.zip REPORT.json --deep --rebuild 02_glb_gratuit_hunyuan2mv/beagle.glb
python lego-builder/tools/simulate_customer_v1.py LEGO_Builder_Beagle_V1_Digital_Kit.zip REPORT.json
lego-builder/tools/product_regression_v1.sh
```
GLB du modèle LEGO : produit par `product_renders_v1.py` (`Beagle_V1.glb`, **304 Mo**, 52 Mo compressé) mais **non inclus** dans le kit ni dans le dépôt (trop lourd) ; empreinte et commande ci-dessus.
