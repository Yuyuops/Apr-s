#!/usr/bin/env python3
"""Product V1 (Beagle) : assemble the self-contained Digital Kit ZIP from already generated artefacts (model, BOM, renders, notice) + user documentation + licence notice + integrity manifest.
usage : build_kit_beagle_v1.py WORK_DIR OUT_ZIP   (WORK_DIR must contain : model/ bom/ renders/ instructions/ validation/ ; see product_v1_beagle/BUILD_COMMANDS.md)"""
import hashlib, json, os, shutil, subprocess, sys, zipfile, datetime
work, out_zip = [os.path.abspath(x) for x in sys.argv[1:3]]; ROOT = "LEGO_Builder_Beagle_V1_Digital_Kit"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
bom = json.load(open(work + "/bom/Beagle_V1_BOM.json")); rep = json.load(open(work + "/instructions/notice_report.json")); eng = json.load(open(work + "/validation/beagle_validation_v2.json"))
N, L, T, S = bom["total_pieces"], bom["part_colour_lines"], bom["distinct_part_numbers"], rep["steps"]; MS = bom["ldraw_sha256"]; ncol = len(bom["colours"]); rare = [l for l in bom["lines"] if l["rarity_proxy"] == "rare"]; rare_all = [l for l in bom["lines"] if l["rarity_proxy"] != "courante"]; rare_txt = ", ".join("%s %s x%d (%d sets)" % (l["part_name"], l["colour_name"], l["quantity"], l["rebrickable_sets_containing_pair"]) for l in rare)
single = eng["single_stud_joints"]; joints = eng["joints"]; tipmin = eng["stability"]["min_tip_force_N"]; lt2 = eng["stability"]["tip_force_below_2N"]; sub1g = eng["stability"]["subassemblies_over_1g"]
mass = sum(l["model_mass_g"] for l in bom["lines"])
DOC = {}
DOC["README.md"] = f"""# LEGO Builder - Beagle V1 - Digital Kit

**Version 1.0.0 (technique)** - modèle LEGO du Beagle : **{N:,} pièces**, **{L} références** (pièce x couleur), **{T} formes**, **{ncol} couleurs**, **{S} étapes** de construction.
Statut : **validé numériquement, PAS encore construit en vrai, PAS commercialisable** (droits et test réel non établis, voir `LICENSES/LICENSES.md` et `docs/LIMITES_CONNUES.md`).

## Par où commencer
1. Ouvrez `docs/GUIDE_UTILISATEUR.md` (le guide pas à pas).
2. Regardez `renders/` (6 vues haute résolution) et `preview/Beagle_V1_turntable.gif` (tour complet).
3. Préparez vos pièces avec `bom/Beagle_V1_BOM.csv` (ou importez `bom/Beagle_V1_rebrickable_import.csv` dans Rebrickable).
4. Construisez avec `instructions/Beagle_V1_Notice.pdf` ({rep['pages']} pages : {rep['front_matter_pages']} pages d'introduction, {S} étapes, 1 page de fin).

## Contenu
| Dossier | Fichiers |
|---|---|
| `model/` | `Beagle_V1.ldr` (modèle complet, SHA-256 `{MS}`), `Beagle_V1_steps.ldr` (mêmes pièces, ordre de montage avec lignes STEP) |
| `instructions/` | `Beagle_V1_Notice.pdf`, `steps.csv` (une ligne par étape : pièces, quantités, couleurs, couches) |
| `bom/` | nomenclature CSV et JSON, liste des références LDraw, import Rebrickable, pièces rares, contrôle de cohérence |
| `renders/` | face, dos, profils gauche et droit, trois-quarts avant et arrière, dessus (PNG 2400 x 2400) |
| `preview/` | tour complet animé (GIF) |
| `validation/` | rapports de validation numérique du moteur (collisions, connexions, stabilité indicative) |
| `docs/` | guide utilisateur, limites connues, fiche de validation humaine à remplir |
| `LICENSES/` | notices de licences et mentions |
| `MANIFEST.json`, `SHA256SUMS.txt` | version, comptes et empreintes SHA-256 de chaque fichier |

English summary: digital kit for a {N:,}-piece LEGO-compatible beagle (LDraw model, PDF instructions with {S} steps, BOM CSV/JSON, renders). Numerically validated only; not physically built; not cleared for commercial sale. Instructions are in French.

*LEGO(R) est une marque du groupe LEGO, qui ne parraine, n'autorise ni ne cautionne ce produit. Les noms de pièces suivent les catalogues publics LDraw et Rebrickable.*
"""
DOC["docs/GUIDE_UTILISATEUR.md"] = f"""# Guide utilisateur - Beagle V1

## 1. Ce que contient le package
Voir le tableau de `README.md`. Tout est autonome : aucun accès à Internet ni à un dépôt n'est nécessaire pour lire le modèle, la nomenclature et la notice.

## 2. Logiciels nécessaires (tous gratuits)
| Besoin | Logiciel possible |
|---|---|
| Lire la notice et les rapports | un lecteur PDF (Adobe Reader, Aperçu, Firefox...) |
| Voir le modèle en 3D (`.ldr`) | **Studio** (BrickLink, gratuit), **LeoCAD** ou **LDView** (libres). Ces logiciels contiennent ou téléchargent la bibliothèque officielle de pièces LDraw. |
| Ouvrir les nomenclatures (`.csv`) | LibreOffice Calc, Excel ou Numbers |
| Voir les rendus et le GIF | n'importe quel navigateur ou visionneuse d'images |
Remarque : le modèle comporte {N:,} pièces ; l'ouverture dans un logiciel 3D peut prendre un moment sur un ordinateur modeste.

## 3. Visualiser le modèle
- **Rapide** : ouvrez les PNG de `renders/` (6 angles) et `preview/Beagle_V1_turntable.gif`.
- **En 3D** : ouvrez `model/Beagle_V1.ldr` dans Studio/LeoCAD/LDView, puis tournez autour du modèle.
- **Étape par étape sur ordinateur** : ouvrez `model/Beagle_V1_steps.ldr` : les lignes STEP délimitent les {S} étapes dans l'ordre de la notice (Studio et LeoCAD proposent un mode « pas à pas »).

## 4. Utiliser la nomenclature (BOM)
- `bom/Beagle_V1_BOM.csv` : une ligne par pièce et par couleur ({L} lignes) avec la quantité, le numéro de pièce, la couleur (nom et numéro), la rareté estimée et la masse théorique. **Total : {N:,} pièces.**
- `bom/Beagle_V1_rebrickable_import.csv` : format « Part, Color, Quantity » (numéros de couleur Rebrickable) à importer dans une liste de pièces Rebrickable.
- `bom/Beagle_V1_ldraw_parts.csv` : références de fichiers LDraw (`.dat`) et numéros de couleur LDraw.
- `bom/Beagle_V1_rare_parts.csv` : les {len(rare_all)} références rares ou peu courantes (30 sets Rebrickable ou moins = rare ; 31 à 100 = peu courante) dont {len(rare)} rare : {rare_txt} : **à chercher en premier**. Attention : c'est un indicateur de rareté, **pas une information de stock ni de prix** : aucun prix, aucune disponibilité n'est fournie dans ce kit.
- Aucun fichier BrickLink n'est fourni (les correspondances de numéros de pièces et de couleurs BrickLink ne sont pas dans nos données) ; à partir de la liste Rebrickable, vérifiez les possibilités d'export sur le site.
- `bom/bom_cross_check.json` : contrôle automatique BOM = modèle (mêmes quantités, aucune différence).
Couleurs utilisées ({ncol}) : """ + ", ".join("%s (%d)" % (c["name"], c["ldraw_id"]) for c in bom["colours"]) + f""".

## 5. Suivre la notice (`instructions/Beagle_V1_Notice.pdf`)
1. Lisez les pages d'introduction : lecture de la notice, liste des pièces, plan, vues du modèle terminé.
2. Triez vos pièces par couleur puis par numéro.
3. Une page = une étape : l'image montre en couleur les pièces à ajouter (les pièces déjà posées sont pâles) ; la liste donne quantité, nom, numéro et couleur ; la phrase sous l'image indique si les pièces se posent simplement ou s'emboîtent, et dans quel sens.
4. Certaines étapes demandent d'emboîter des pièces **par en dessous** (indiqué « vers le haut ») : soutenez ou retournez le modèle avec précaution.
5. 13 petits détails du visage se construisent à part (« Construire à part »), puis se fixent (« Fixer sur le modèle »).
6. À la fin, comparez avec la page « Le modèle terminé » et vérifiez que vous avez posé {N:,} pièces.
`steps.csv` reprend chaque étape sous forme de tableau (pièces `quantitéxnuméro@couleur LDraw`, couches).

## 6. Limites connues
Voir `docs/LIMITES_CONNUES.md` (à lire avant de commencer) et remplissez `docs/FICHE_VALIDATION_HUMAINE.md` après votre construction.
"""
DOC["docs/LIMITES_CONNUES.md"] = f"""# Limites connues - Beagle V1

1. **Jamais construit en vrai.** La validation est **numérique** : 0 collision, 0 pièce déconnectée, 0 îlot, 0 pièce sans appui (validateur indépendant du moteur) ; ce n'est pas un test physique. Des erreurs de notice, de pièces ou de tolérances peuvent apparaître à la construction.
2. **Modèle très fragile à la manipulation.** Sur {joints:,} liaisons, {single:,} ({100 * single / joints:.0f} %) tiennent par un seul tenon. Estimation théorique indicative : {sub1g} sous-ensembles de plus de 1 g, {lt2} cas de force de bout inférieure à 2 N (minimum {tipmin} N). Manipulez par le corps, jamais par les oreilles, la queue ou les pattes ; ne le déplacez pas avant la fin du montage complet.
3. **Pièces et couleurs.** Le modèle utilise {ncol} couleurs et {T} formes de pièces ; certaines références sont peu courantes (voir `bom/Beagle_V1_rare_parts.csv`), notamment les plaques 4 x 6 Dark Orange (945 pièces). Aucune disponibilité ni aucun prix n'est vérifié. Les couleurs sont les plus proches du catalogue, pas une copie exacte du chien d'origine.
4. **Notice.** Texte en français ; noms de pièces en anglais (catalogue LDraw). Les images des étapes ont un angle fixe et sont cadrées sur la zone en cours : l'orientation exacte de chaque pièce se lit sur l'image. 147 étapes sur {S} comportent des pièces à emboîter par en dessous (« vers le haut ») et l'étape 447 (museau) s'insère de l'avant vers l'arrière du chien : ce sont les étapes les plus susceptibles d'être ambiguës. Aucune étape ne demande de chemin d'insertion avec virages.
5. **Fabrication expérimentale** (STL/3MF) : non incluse dans ce kit ; aucune compatibilité avec une imprimante n'est validée.
6. **Droits.** Ce kit n'est pas déclaré commercialisable : voir `LICENSES/LICENSES.md`.
"""
DOC["docs/FICHE_VALIDATION_HUMAINE.md"] = """# Fiche de validation humaine (à remplir après construction)

Testeur : ____________   Date : ____________   Expérience LEGO : débutant / intermédiaire / expert

| # | Question | Réponse (oui / non / remarque) |
|---|---|---|
| 1 | Le ZIP s'ouvre et les fichiers se comprennent sans aide | |
| 2 | Le guide utilisateur est clair | |
| 3 | Les rendus permettent de reconnaître le modèle fini | |
| 4 | J'ai pu rassembler toutes les pièces de la liste (lesquelles manquent ?) | |
| 5 | Quelles pièces ou couleurs ont été difficiles à trouver ? | |
| 6 | Temps passé à préparer/trier les pièces | |
| 7 | Étapes ambiguës (numéros d'étape + description) | |
| 8 | Étapes impossibles ou pièces qui ne s'emboîtent pas (numéros) | |
| 9 | Étapes où il faut emboîter par en dessous : étaient-elles compréhensibles ? | |
| 10 | Le modèle terminé tient-il à la manipulation normale ? Pièces qui se détachent (où ?) | |
| 11 | Total de pièces posées = 10 567 ? Pièces restantes / manquantes | |
| 12 | Temps total de construction | |
| 13 | Le modèle terminé ressemble aux rendus | |
| 14 | Commentaires libres | |
"""
DOC["LICENSES/LICENSES.md"] = """# Licences et mentions - Beagle V1 Digital Kit

**Ce kit n'est pas déclaré commercialisable.** Les droits sur le modèle source n'ont pas été établis (voir ci-dessous). Ce texte n'est pas un avis juridique.

| Élément | Origine | Condition connue | Statut |
|---|---|---|---|
| Géométrie des pièces (rendus, noms) | Bibliothèque LDraw (ldraw.org), non copiée dans le kit | CC BY (4.0 selon le verrouillage du projet) : citer LDraw.org | mention fournie |
| Numéros de couleurs, années, nombre de sets par pièce | Base de données Rebrickable (rebrickable.com) | conditions d'usage Rebrickable à vérifier avant diffusion ; mention « Données : Rebrickable.com » | à vérifier |
| Modèle du Beagle (forme, couleurs) | reconstruction 3D par Tencent Hunyuan3D-2mv à partir de 4 images de référence puis conversion en briques | licence communautaire Tencent Hunyuan 3D 2.0 : **ne s'applique pas dans l'Union européenne, le Royaume-Uni et la Corée du Sud** (« unlicensed and unauthorized » hors territoire) ; Tencent ne revendique pas de droits sur les sorties | **BLOQUANT à clarifier (juriste)** |
| Images de référence du Beagle | fournies au projet (rendus de LEGO selon `CONTROLE_COHERENCE`), origine et droits non documentés | inconnu | **non établi** |
| Marque LEGO(R) | groupe LEGO | ne parraine ni n'autorise ce produit ; usage du mot LEGO dans un nom commercial à examiner | à examiner |
| Notice PDF, BOM, documents | génération par les outils du projet (Python, ReportLab, Pillow) | licence du dépôt non déclarée | à décider |
"""
for rel, txt in DOC.items():
    os.makedirs(os.path.dirname(os.path.join(work, rel)) or work, exist_ok=True); open(os.path.join(work, rel), "w").write(txt)
# manifest + hashes
files = sorted(os.path.relpath(os.path.join(d, f), work) for d, _, fs in os.walk(work) for f in fs if f not in ("MANIFEST.json", "SHA256SUMS.txt") and not f.startswith("."))
git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
man = dict(product="LEGO Builder - Beagle V1 Digital Kit", version="1.0.0-technical", built_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), source_repo_commit=git, model_ldraw_sha256=MS,
           counts=dict(pieces=N, part_colour_lines=L, distinct_part_numbers=T, colours=ncol, steps=S, notice_pages=rep["pages"]), notice=dict(front_matter_pages=rep["front_matter_pages"], steps=S, main_steps=rep["main_steps"], sub_assembly_steps=rep["sub_assembly_steps"], attach_steps=rep["attach_steps"]),
           engine="LEGO sculpture engine V12.1 (validated, see validation/)", validation_status="numeric validation only; no physical construction test", commercial_status="NOT commercial: rights and human/physical validations not established",
           files=[dict(path=f, bytes=os.path.getsize(os.path.join(work, f)), sha256=sha(os.path.join(work, f))) for f in files])
json.dump(man, open(os.path.join(work, "MANIFEST.json"), "w"), indent=1)
with open(os.path.join(work, "SHA256SUMS.txt"), "w") as f:
    for rel in sorted(files + ["MANIFEST.json"]): f.write("%s  %s\n" % (sha(os.path.join(work, rel)), rel))
if os.path.exists(out_zip): os.remove(out_zip)
with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for rel in sorted(files + ["MANIFEST.json", "SHA256SUMS.txt"]): z.write(os.path.join(work, rel), ROOT + "/" + rel)
print(json.dumps(dict(zip=out_zip, bytes=os.path.getsize(out_zip), files=len(files) + 2, sha256=sha(out_zip))))
