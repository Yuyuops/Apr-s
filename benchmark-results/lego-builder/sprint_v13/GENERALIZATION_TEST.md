# Sprint V13 — C : protocole reproductible pour un sujet jamais vu (4 photos)

**Statut : protocole prêt, outil testé à vide ; AUCUN sujet inédit n'a encore été exécuté — les photos n'ont pas été fournies.** Les reconstructions historiques Paco/Beagle (y compris « Beagle sans déclarer le sujet ») **ne sont pas une preuve de généralisation** : elles ont servi à développer le moteur. L'outil refuse d'ailleurs de présenter un sujet connu comme preuve (le test a été vérifié : photos Paco → `REFUSED`).

## Commande (une seule)
```
python tools/generalization_test.py OUT_DIR face.png dos.png profil_gauche.png profil_droit.png [--size-mm 400] [--runs 2]
```
Prérequis : accès huggingface.co (Hunyuan3D-2mv), `gradio_client`, installation du moteur 1 (`LEGO_ENGINE_HOME`). Photos détourées (RGBA) ou fond uniforme ; vues reconnues par leur nom. Le script exécute `python -m lego_builder run --photos … --notice fast --pdf` **deux fois** (dossiers `run1`, `run2`), mesure, écrit `generalization_result.json`.

## Mesures et seuils (fixés AVANT l'exécution, non modifiables après)
| Axe | Mesure | Seuil de réussite |
|---|---|---|
| Fidélité géométrique | IoU d'occupation modèle/GLB (`audit_fidelity.py`, global + par zone) | IoU global ≥ 0,75 (réf. Paco 0,867, sujet de développement) |
| Fidélité couleur | ΔE76 moyen vs GLB, plancher palette, cellules parasites, part sans correspondance | ΔE ≤ 20 ; parasites ≤ 5 % (réf. Paco : 15,5 ; 1,9 %) |
| Reproductibilité | même photos → même GLB ? même LDraw (SHA-256) ? nombre de pièces, durée des deux runs | **rapportée, non présumée** (l'espace HF peut être non déterministe) |
| Constructibilité | validateur indépendant : collisions, pièces déconnectées, îlots, non supportées = 0 ; rapport de fragilité ; pièces / références | 0 / 0 / 0 / 0 |
| Temps | durée de bout en bout de chaque run | rapportée (réf. Paco : ≈ 4 min moteur + reconstruction HF ≤ 8 min) |
| Qualité de la notice | nombre d'étapes, notice LDraw + PDF produits | ≥ 10 étapes, PDF présent (relecture humaine en plus) |

Résultat : `PASS` seulement si validateur PASS **et** IoU **et** ΔE **et** notice sont tous au seuil ; sinon `FAIL` ; `BLOCKED` si aucun run n'aboutit. Deux sous-verdicts à lire séparément : *constructibilité* (le moteur construit toujours quelque chose de valide) et *fidélité* (ressemble-t-il au sujet ?). La ressemblance finale se juge aussi **visuellement** (face/profil/dos vs photos), non automatisable.

## Vérification à vide (sans nouveau sujet)
La fonction de mesure appliquée à un projet existant (Paco, photos → LEGO) redonne : 3 193 pièces, 89 références, ΔE 15,5, IoU 0,867, LDraw `9d07c041…` = V12.1, 370 étapes de notice. Le chemin de mesure fonctionne ; **le test de généralisation reste à faire avec des photos d'un sujet nouveau** (décision/entrée humaine requise : fournir les quatre photos).
