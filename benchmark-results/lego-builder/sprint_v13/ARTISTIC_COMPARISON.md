# Sprint V13 — Comparaison artistique avant / après (A1 Italy, A2 Paco, A3 Beagle)

Grille inchangée (5 critères /5, total /25, aucun critère < 3). **Notation interne, subjective, faite par le modèle** : elle ne remplace pas un regard humain (voir « Limites »). Aucune métrique n'a été modifiée pour « gagner » : même composition `italia_portrait_64x96` (grille 96 × 64 plots), mêmes règles de validation, mêmes critères.

## A1 — Italy Premium (baseline 19/25 → 3 cycles, meilleur = C3)

| Cycle | Modification minimale (style JSON uniquement) | Pièces | Réf. | Génération (build / validation / rendu) | Stabilité (1 tenon / porteuses / pts d'articulation) | Validateur | Notation |
|---|---|---|---|---|---|---|---|
| Baseline `premium_noyer_or_lagon_c2i` | — | 13 633 | 111 | — | 1 092 / 408 / 976 | PASS | **19** (4 · 3 · 4 · 4 · 4) |
| **C1** relief terrestre | bandes intérieures `land_inland_widths_studs=[4,10]` + rampe de teintes terre `{84, 28, 70}` | 13 873 | 131 | 6 s / 35 s / rendu 3 vues ≈ 55 s | 1 212 / 436 / 1 052 | PASS (0 collision, 0 déconnecté, 0 îlot, 0 non supporté) | 20 (4 · 4 · 4 · 4 · 4) |
| C2 hiérarchie des mers | + mers `{4:323, 3:322, 2:212, 1:321}`, fond 321 | 11 694 | 177 | 5 s / 27 s / ≈ 64 s | 1 173 / 401 / 1 015 | PASS | 19 (4 · 4 · **3** · 4 · 4) — taches bleu foncé isolées, ton saturé trop dur par endroits |
| **C3** (retenu) | C2 sans la teinte 321 : mers `{4:323, 3:322, 2:212, 1:212}`, fond 212 | **13 354** | 155 | 5 s / 28 s / ≈ 62 s | **1 174 / 402 / 989** (mieux que la baseline) | PASS | **21** (**5** · 4 · 4 · 4 · 4) |

Détail C3 (rendus `renders/italy_c3_*.jpg`, comparaison `renders/italy_before_after_face.jpg`) :
- *Lisibilité géographique 4 → 5* : le liseré aqua clair sépare nettement terre et mer ; la bande « boueuse » grise de la baseline est remplacée par un dégradé aqua → turquoise → bleu clair lisible à distance normale.
- *Relief / hiérarchie 3 → 4* : la terre n'est plus plate ; trois niveaux (côte, plateau, dorsale taupe) font apparaître l'épine apennine et les Alpes. Reste imparfait : taupe un peu terne, pas de transition adoucie entre niveaux (le moteur n'a que des paliers de 3 plaques).
- *Harmonie couleurs 4* (inchangé) : turquoise saturé contre bruns chauds = complémentaires, acceptable ; le taupe reste un peu sourd.
- *Cadre / typographie 4* (inchangé) : non retouchés (le 3ᵉ cycle a été consacré à corriger la dérive de C2, pas au cadre).
- *Esthétique d'ensemble 4* (inchangé).

Reproductibilité C3 : deux constructions successives donnent le même `diorama.ldr` (SHA-256 `b34e4ef8…`, `italy_v13c3/SHA256.txt`). Fichiers : `italy_v13c3/` (LDraw, liste de pièces, métriques, validation indépendante, fragilité, 3 styles C1–C3). Le style C3 **n'est pas encore une référence CI** : la baseline `ci/reference_hashes.json` est inchangée et reste bloquante (run Maps 42510458950 : succès, étape SHA-256 bloquante PASS).

**Décision A1 : seuil ≥ 20/25 atteint sur la grille inchangée (21/25 auto-évalué) → GO artistique *sous réserve* d'une validation visuelle humaine** (un score auto-attribué n'est pas une preuve commerciale). Si la lecture humaine ne confirme pas ≥ 20, la décision redevient NO-GO artistique ; la baseline reste intacte.

## A2 — Paco (V12.1 conservé)

Leviers testés **sans toucher au moteur** (config sujet), tous rejoués depuis le GLB, comparés au modèle accepté V12.1 (`paco_V121_A_palette_V12/paco_brut.ldr`, SHA `9d07c041…`) :

| Variante | LDraw identique à V12.1 ? | ΔE moyen (plancher moteur 13,0) | Cellules parasites | IoU global | Décision |
|---|---|---|---|---|---|
| Rejeu V12.1 (config inchangée) | **oui, octet pour octet** | 15,5 | 114 | 0,867 | référence |
| `max_colours` 10 | identique | 15,5 | 114 | 0,867 | aucun effet |
| `max_colours` 12 | identique | 15,5 | 114 | 0,867 | aucun effet |
| bouche variante A | non | 15,6 | 114 | 0,867 | rejetée (≤ V12.1) |
| bouche variante B | non | 15,5 | 116 | 0,865 | rejetée (≤ V12.1) |

Cause : la sélection de palette s'arrête d'elle-même — tout candidat supplémentaire apporte un gain ΔE de 0,00 < 0,8 (`palette.json: meilleurs_candidats_refuses`). La fidélité couleur est au plancher de la palette (15,5 vs 13,0 moteur vs 11,4 catalogue entier) ; l'écart restant vient de la quantification volumique, pas du choix des couleurs. Pour la bouche, la lisibilité n'est pas meilleure sur les 4 vues (`renders/paco_views_ref_v121_mouthB.jpg` : GLB | V12.1 | variante B ; face, profil droit, trois-quarts, dos). Améliorer réellement la bouche demande un changement de moteur (lèvre courbe non implémentée, cf. `15_mouth_and_cavities/VERDICT.md`), hors périmètre « corrections locales à config ». **Paco V12.1 conservé, aucune référence modifiée.** Données : `paco_variants/`.

## A3 — Beagle
Aucune modification du moteur ni de la config ⇒ aucune régression possible hors CI ; la non-régression Beagle V12.1 reste bloquante dans `lego-builder-regression.yml`.

## Limites
- Notation auto-attribuée, une seule vue de référence humaine absente ; ± 1 point d'incertitude par critère.
- Italy : le palier de relief est discret (3 niveaux), pas de dégradé continu ; cadre/typographie non améliorés.
- Paco : mâchoire/lèvre et ΔE restent perfectibles (limite moteur, pas config).
