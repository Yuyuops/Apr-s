# Revalidation des moteurs (2026-11-08)
Branche `research/lego-builder-commercial-outputs-20261108`. Les statuts reposent sur des **exécutions réelles** (CI GitHub Actions et mesures locales de cette session), pas sur les rapports antérieurs. Verdicts : PASS / FAIL / BLOCKED (cause indiquée).

## Exécutions de référence
| Exécution | Contenu | Résultat |
|---|---|---|
| CI cartes `lego-maps-v09-deliverables`, run 42243682363 (branche photos) | régénère 8 modèles de cartes, comparaison **bloquante** des SHA-256 | **succès**, 8 identiques |
| CI `lego-builder-regression`, run 42256747041 | Paco et Beagle depuis le GLB, Paco depuis les 4 photos (Hunyuan3D-2mv), comparaison bloquante des SHA-256 | **succès** (sculpture-regression 20 min, photos-to-lego 5 min) |
| Local : `geo` Italie, `run` Hyrule/UK, `run --photos` Paco/Beagle | voir mesures | voir tableau |

## Tableau
| Moteur / critère | Statut | Preuve |
|---|---|---|
| **Maps** : collisions, connexions, îlots, supports au placement | **PASS** | `delivery_check` des 8 modèles : 0 collision, 0 pièce déconnectée, 0 îlot, 0 non supporté |
| Maps : non-régression | **PASS** | 8 LDraw identiques (SHA-256) en CI, étape bloquante |
| Maps : BOM / plan / notice cohérents | **PASS** | LDraw = `parts.json` = `parts_list.csv`, plan = modèle (492 étapes Italie) |
| Maps : validateur indépendant (LDraw Nova) | **PASS** | 0 recouvrement de corps, Italie, Hyrule : 0 pièce isolée (optimiste), voir `NOVA_EVALUATION.md` |
| Maps : solidité (supports critiques) | **FAIL (indicatif)** | Hyrule biomes : 1 898 pièces à un tenon (1 050 porteuses), 1 532 points d'articulation ; Italie : 1 092 (408), 976. Pas d'essai physique |
| Maps : esthétique Premium | **FAIL** | Italie 19/25 < 20 (grille Premium, notation interne) ; Écosse 17, Japon 18, Royaume-Uni 17 ; Hyrule non noté. Aucun gain tenté dans cette session |
| Maps : fidélité visuelle de face / oblique | **BLOCKED** | revue humaine indépendante nécessaire ; les rendus existent (`livraison_v08/`, `livraison_v10/`) |
| **Sculptures** Paco : forme/couleurs | **PASS** (limité) | LDraw identique au modèle accepté V12.1 (SHA `9d07c041…`) ; IoU silhouette 0,895 ; ΔE76 28,9 |
| Paco : collisions, tenons bloqués | **PASS** | 0 collision, 0 tenon bloqué, catalogue complet, 8 cas faibles (idem V12.1) |
| Paco : notice et nomenclature | **PASS** | plan rapide 207 étapes en 525 s, 0 contrôle en défaut ; pièces `main` 2 544 + `sub` 649 = 3 193 = modèle ; nomenclature 3 193 |
| Paco : bouche et couleurs « perfectibles » | **FAIL (connu)** | non amélioré ; détails du visage moins nets sans configuration validée |
| Paco : solidité | **BLOCKED** | pas d'essai physique ; 8 cas faibles, 2 995 jonctions à un tenon |
| Beagle : forme/couleurs | **PASS** (limité) | identique à V12.1 ; IoU 0,945 ; ΔE76 32,9 ; 0 cas faible |
| Beagle : validateur indépendant | **PASS avec réserve** | Nova : 0 recouvrement ; 2 pièces non reliées (6141, 3960) : coupoles inversées, voir Nova |
| **Photos → GLB** : reproductibilité | **PASS** | GLB reconstruit identique au `paco.glb` et au `beagle.glb` (sommets, faces, couleurs) ; LDraw identique à V12.1 sans option (empreinte de géométrie) ; CI 5 min |
| Photos → GLB : sujet quelconque, fidélité | **BLOCKED** | aucune photo d'un autre sujet dans le dépôt ; **NO-GO maintenu** pour une conversion arbitraire |
| Photos → GLB : service externe | **FAIL puis corrigé** | 1ʳᵉ exécution CI bloquée 1 h (Space Hugging Face sans réponse) ; délai de 480 s par tentative ajouté ; 2ᵉ exécution réussie |
| **Builder** : 8 modèles identiques | **PASS** | CI, étape bloquante |
| Builder : temps | **PASS** | Italie `geo` 97 s ; Hyrule 400 mm 32 s ; Paco 125-150 s ; notice rapide 525 s |
| Disponibilité, prix, coût d'approvisionnement | **BLOCKED** | aucune source de prix ou de stock accessible ; aucun budget donné |
| Validation physique (emboîtement, tenue) | **BLOCKED** | pas d'imprimante ni de pièces physiques |

## Défauts réels trouvés et corrigés dans cette campagne
1. `lego_run.py` : l'étape de notice `--all` cherchait une séquence pour tout le modèle (plus de 20 minutes) → option `--notice-ears sub` (défaut inchangé), délai dur côté builder.
2. Photos → GLB : appel au Space sans délai → délai par tentative, diagnostic explicite (file d'attente, quota).
3. Cartes : filets de cadre de longueur impaire faisaient planter le générateur (carte non carrée) → corrigé, modèles existants identiques.
4. CI : comparaison de SHA-256 « rapport seulement » → **bloquante**.

## Non fiabilisé (explicite)
Esthétique des cartes (19/25), bouche et couleurs de Paco, solidité, sujet inconnu. Aucune de ces limites n'a été masquée par une modification des références.
