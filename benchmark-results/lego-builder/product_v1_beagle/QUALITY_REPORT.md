# Product V1 Beagle — Rapport de qualité

## 1. Audit du Beagle validé (avant génération)
| Élément | Constat | Preuve |
|---|---|---|
| Version validée | **Beagle V12.1** (`22_color_structural_regression/modeles/beagle_V121/`) ; verdict V12.1 : « objectifs atteints » pour le Beagle | `VERDICT.md` (V12.1) |
| Modèle LDraw | `beagle_brut.ldr`, **10 567 pièces**, SHA-256 **551bde0f…808f** = empreinte de référence du CI (`ci/reference_hashes.json`, `beagle_V121`) | recalculé |
| Reproductibilité | `lego_builder run beagle.glb` → LDraw **identique** (3 fois : régression, validateur, run avec notice) | `regression/08`, `09` |
| Références / couleurs | **64** lignes (23 formes x 5 couleurs) ; 0 paire hors catalogue | `bom_verification.json` |
| Validation moteur | 0 collision, 0 bloqué, 0 pièce déconnectée, 0 îlot, 0 sans appui ; 20 594 liaisons dont 9 715 à un tenon ; force de bout minimale 0,52 N, 0 cas < 0,5 N ; 0 groupe faible (indicatif, non physique) | `beagle_validation_v2.json`, `beagle_weak.json` |
| Rendus existants | planches de comparaison V11/V12/V12.1 900 px (pas de rendus propres) | `rendus/beagle_*.png` |
| Notice existante | plan (554 étapes) et CSV, **pas de PDF** ; le PDF natif du moteur est titré « Paco » (non utilisé) | `notices/beagle_V121/` |
| Statut moteur de sculpture | **non modifié** | git |

## 2. Contenu généré (`LEGO_Builder_Beagle_V1_Digital_Kit.zip`)
| Livrable | Détail | Statut |
|---|---|---|
| Modèle LDraw | `Beagle_V1.ldr` (référence), `Beagle_V1_steps.ldr` (ordre de montage, 554 étapes) | **PASS** |
| Rendus | 7 vues PNG 2400 x 2400 (face, dos, profils G/D, trois-quarts avant et arrière, dessus) | **PASS** |
| Prévisualisation | tour animé GIF (12 vues) | **PASS** |
| GLB | produit (304 Mo, 52 Mo compressé, SHA-256 `2144cb1b…`), **non inclus** (trop lourd pour le kit et le dépôt) | **PARTIEL** |
| Notice PDF | 561 pages, 554 étapes, recherchable, titres corrects | **PASS** (numérique) |
| BOM | CSV, JSON, LDraw, Rebrickable, pièces rares, contrôle croisé ; pas de prix | **PASS** |
| Guide, limites, fiche humaine, licences | Markdown | **PASS** |
| Manifeste | `MANIFEST.json`, `SHA256SUMS.txt` (28 fichiers) | **PASS** |

## 3. Validateur automatique (`tools/validate_product_v1.py`, sur le ZIP livré)
| # | Contrôle | Résultat |
|---|---|---|
| 1 | Fichiers obligatoires | **PASS** (29 fichiers) |
| 2 | Intégrité (testzip, SHA256SUMS, manifeste) | **PASS** |
| 3 | BOM = modèle (CSV, JSON, LDraw, Rebrickable, fichier d'étapes) | **PASS** (10 567, 64 lignes) |
| 4 | Notice = pièces (étapes vs BOM, pages, lignes de chaque page) | **PASS** (554 étapes, 561 pages) |
| 5 | Références reconnues (.dat, couleurs, paires Rebrickable) | **PASS** |
| 6 | Pas de collision critique (validateur du moteur relancé sur le LDraw livré) | **PASS** (0 collision, 0 bloqué) |
| 7 | Pas de pièce déconnectée / îlot / sans appui (fichier d'étapes) | **PASS** (0 / 0 / 0) |
| 8 | Génération reproductible (GLB → LEGO, SHA-256 identique) | **PASS** |
| 9 | SHA-256 des livrables | **PASS** (28 fichiers) |
| 10 | Pas de régression des autres moteurs | **PASS** (voir `REGRESSION_REPORT.md`) |
Anomalie trouvée par le validateur : `Beagle_V1.ldr` (ordre de fichier arbitraire) signale 353 « pièces sans appui au moment de la pose » ; c'est un artefact d'ordre (0 pour le fichier d'étapes, ordre de montage) : le critère 7 est jugé sur le fichier d'étapes, l'écart est documenté.

## 4. Fabrication expérimentale (séparée : `LEGO_Builder_Beagle_V1_EXPERIMENTAL_Print_Files.zip`, 12 Mo)
STL/3MF produits par les exporteurs existants : briques individuelles (10 547 pièces sur 10 567, 88 plateaux, 18 STL + 10 3MF), 4 modules imprimables (+ variante suivant l'enveloppe LDraw), 22 pièces de test de tolérances. **Validation numérique : PASS** (solides étanches, 3MF bien formés, ≤ 250 mm, 0 chevauchement ; `experimental_print/numeric_validation.log`). **Bambu Studio : non ouvert, aucune impression : compatibilité Bambu NON validée (BLOCKED).** Masse et temps = formules (borne haute 8,9 kg / 258 h en briques ; modules ≈ 113 h à 30 % de remplissage), pas un tranchage.

## 5. Limites
Aucune construction réelle ; notice non lue par une personne extérieure ; 147 étapes par en dessous ; coût et disponibilité non vérifiés ; droits non établis (`LICENSE_REVIEW.md`).
## 6. Cycles de correction (maximum 2)
Cycle 1 : notice native du moteur titrée « Paco » → notice recomposée avec les bons titres ; critère 7 du validateur corrigé (ordre de fichier). Cycle 2 : directions d'insertion (haut/bas/museau) et textes de rareté/limites corrigés. Aucune modification des moteurs.
