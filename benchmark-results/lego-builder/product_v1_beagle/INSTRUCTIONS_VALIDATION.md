# Product V1 Beagle — Validation de la notice

Notice : `instructions/Beagle_V1_Notice.pdf` (561 pages A4 : 6 pages d'introduction, **554 étapes**, 1 page finale ; texte recherchable), `instructions/steps.csv`. Générée par `tools/product_notice_v1.py` **à partir du plan du moteur validé (V10+) et de ses rendus d'étapes** : ordre, pièces par étape et contrôles d'emboîtement viennent du moteur ; ce script ne re-planifie rien.

## Structure
- 528 étapes « corps » (≤ 20 pièces par étape, couche après couche : 125 couches de plaques), 13 étapes « construire à part » (petits détails du visage, 14 pièces) suivies de 13 étapes « fixer sur le modèle ». 10 553 + 14 = **10 567 pièces posées**.
- Chaque page : numéro d'étape, avancement (pièces posées / 10 567), image du modèle en cours (pièces posées pâles, pièces à ajouter en couleur, sous-ensembles décalés), liste quantité x nom (numéro) couleur avec échantillon, phrase d'emboîtement (« se POSENT », « à EMBOÎTER vers le bas / le haut… »).

## Contrôles automatiques (exécutés, ZIP livré)
| Contrôle | Résultat |
|---|---|
| Étapes numérotées 1…554 sans trou | **PASS** |
| Pièces x couleur sommées sur les étapes (hors « fixer ») = BOM | **PASS** (10 567) |
| Plan reconstruit = CSV d'étapes du moteur (références par numéro de pièce, 554 étapes) | **PASS** : 0 étape différente |
| Pages du PDF = 6 + 554 + 1 | **PASS** : 561 |
| Chaque page d'étape imprime son en-tête et chaque ligne (quantité, numéro, couleur) | **PASS** (extraction de texte du PDF, toutes les pages) |
| Parcours client simulé : montage virtuel dans l'ordre de la notice contre le stock de la BOM | **PASS** : jamais de pièce hors stock, sous-ensemble construit avant d'être fixé, stock final = 0 |
| Contrôles d'emboîtement/dégagement du moteur | 0 étape en défaut (`etapes_avec_controle_en_defaut: 0`) |

## Anomalies du moteur trouvées (non corrigées dans le moteur ; contournées dans le produit)
1. Le PDF natif du moteur porte le titre **« Paco cartoon 400 mm - notice V9.1 »** et le libellé de section « Pieds, jambes, bassin, torse, cou et tete » sur toutes les étapes (valeurs figées pour Paco) ; il est en images sans texte. **Non utilisé** : la notice du produit recompose les pages avec les mêmes images d'étapes et les bons titres.
2. L'en-tête du fichier `beagle_notice.ldr` du moteur s'intitule `paco_V9_notice` ; l'en-tête est corrigé dans `Beagle_V1_steps.ldr` (lignes de pièces inchangées, vérifié identique au modèle).
Reproduction : `python -m lego_builder run beagle.glb --notice full` puis `engine/make_notice_pdf.py` sur le plan produit (voir `BUILD_COMMANDS.md`).

## Points d'ambiguïté potentiels (à valider par un humain)
- **147 étapes sur 554** demandent d'emboîter des pièces **par en dessous** (« vers le haut » : 991 pièces, 1 275 pièces marquées « suspendues » par le moteur) : phrase d'avertissement présente, mais ce sont les étapes les plus difficiles à suivre (dont les étapes 4 à 8, au début).
- **Étape 447** (museau : disque 4 x 4 inversé 3960 + plaque ronde 6141) : sens indiqué « de l'avant vers l'arrière du chien ».
- L'angle de vue est fixe et la vue est cadrée sur la zone en cours : l'orientation d'une pièce se lit sur l'image ; aucune annotation manuelle de repère n'a été ajoutée.
- Noms de pièces en anglais (catalogue LDraw), texte de la notice en français.
**Aucune construction physique n'a été faite** : la cohérence est vérifiée par machine, pas par un constructeur.
