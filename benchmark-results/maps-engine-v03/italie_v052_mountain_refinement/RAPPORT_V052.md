# LEGO Maps Italie V0.5.2 — raffinement ciblé de la montagne

Point de départ : commit `1ac0552` (V0.5.1). Diorama local uniquement, Colisée inchangé (même code, même graine : mêmes comptes de murs/arches, 42 arches, 8 fentes). Aucun essai physique ; aucune mesure ci-dessous n'est une preuve mécanique.

## 1. Diagnostic de la V0.5.1 (avant modification)
- **Dôme** : un seul massif de 5 sommets fusionnés par une loi radiale (puissance 2, base ~25 tenons) → une pyramide à un sommet dominant ; profil de flanc = une seule bosse (`montagne_flanc`).
- **Anneau** : une pente 45° posée sur *chaque* marche d'une brique (probabilité 0,92 partout) → couronne régulière de pentes grises/vertes tout autour du sommet.
- **Vallées absentes** : aucun creusement ; les cols entre sommets étaient comblés.
- **Couleurs** : neige = une seule plaque blanche (~40 % du massif) ; brun rouge dominant en bandes ; « Sand Green » vert pâle en liseré artificiel entre herbe et roche ; plage = tuiles tan isolées en damier.
- **Contour** : quasi carré.
- **Fragilité décorative** : arbres à tronc 1×1 et couronne 2×2 (12 arbres, 26 pièces tenues par un tenon sous la couronne), 27 rochers 1×1 sur un tenon.

## 2. Ce qui a été fait (V0.5.2, `terrain.py`)
1. **4 sommets distincts** (rayons 6–7,5 tenons, hauteurs 28 → 87 mm au sommet de brique), flancs concaves irrégulièrement déformés, cols par arêtes limitées (la paire est/sud-ouest n'est pas reliée → vallée profonde).
2. **Deux vallées creusées** (axe sud et échancrure nord) → prairie et forêt entre les volumes.
3. **Falaises réparties** : dénivelés de 2–3 briques autorisés seulement en altitude (> 14 plaques) ; pentes 45° posées avec probabilité 0,62 sur la roche/neige (falaises brisées) et 0,93 sur l'herbe.
4. **Contour** : ellipse tournée de 28° avec baies, plage tan/dark tan continue.
5. **Matières** : neige seulement au-dessus de ~23 plaques, striée de gris clair ; roche en strates (dark tan toutes les 3 couches) ; talus d'éboulis (dark tan/gris/vert foncé) à ≤ 2,2 tenons de la roche ; **plus aucun vert pâle (Sand Green supprimé)** ; herbe vive dans les vallées, vert foncé en altitude ; dunes de sable en bord de mer.
6. **Micro-relief** : 30 plaques de 1–2 plaques de hauteur sur sommets plats ; terrasses 2×2 sur les basses pentes.
7. **Arbres** : 5 conifères *solides* (rond 2×2 3941 + cône 2×2 3942c, 4+4 tenons) sur terrasse plane et 13 arbres *décoratifs* (tronc 1×1, couronnes 2×2).

## 3. Validations (inchangées, aucun seuil modifié) — `results/diorama_v052/independent_validation.json`
2 720 pièces, **0 collision, 0 pièce déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué** ; LDraw = JSON = nomenclature = 2 720. Références : 134/134 `.dat` réels et non-alias, couleurs valides (Rebrickable + LDConfig), **134/134 couples catalogués** (`bom_verification.csv`) ; 3 couples absents du catalogue remplacés par la couleur voisine (8 pièces : 3037/3038 Dark Tan→Tan, 6141 Dark Green→Green). Prix/stock : non vérifiés. Notice PDF non régénérée (non demandée ; le moteur de notice V0.2 n'est pas branché sur ce générateur).

## 4. Fragilité (indicative, modèle rigide du validateur, 1 N/tenon supposé) — `fragility.json`
| | V0.5.1 | V0.5.2 |
|---|---|---|
| Pièces tenues par 1 seul tenon vers le bas | 703 | 855 |
| … feuilles décoratives (ne portent rien) | 242 | 305 |
| … portant d'autres pièces | 461 | 550 |
| Points d'articulation (la perte isole ≥ 1 pièce) | 433 | 530 |
| Pire défaillance isolée (masse coupée de la base) | 7,5 g (mer) | 11,7 g (mer, 20 pièces) |
| Montagne : plus grosse perte sur un point | 9 pièces / 5,1 g | 10 pièces / 4,8 g |
| Murs du Colisée à 1 tenon d'épaisseur | 193 | 193 (inchangé) |

Lecture : aucun sous-ensemble lourd ne dépend d'un seul tenon (≤ 12 g dans tous les cas), mais le relief plus découpé augmente les briques 1×N empilées (+95 pièces à un tenon, dont +63 décoratives). **Décoratif seulement** : 305 feuilles à un tenon (rochers 19, buissons 7, plaques de micro-relief 27 sur un tenon, plage, arbres décoratifs : tronc 1×1 porteur de 2 couronnes, 26 pièces à un tenon, ≤ 2,4 g). **Acceptable structurellement** : conifères solides (4 tenons par étage), pentes (2 tenons ou plus pour 249 des 301), socle et mer. **À renforcer avant tout usage réel** : murs du Colisée à 1 tenon, briques 1×1/1×2 empilées dans la montagne.

## 5. Rendus et comparatifs
`results/diorama_v052/renders/` : `full_face`, `full_trois_quarts`, `full_profil`, `full_rotation_180`, `montagne_face/trois_quarts/sommet/flanc`, `colisee_*`. Comparatifs : `comparatifs/V051_vs_V052_*.png` (ensemble, montagne face / trois-quarts / flanc / sommet, Colisée, profil).

## 6. Auto-critique
Progrès net sur dôme/anneau/vallées/couleurs. Limites visibles : le sommet sud-ouest (29 mm) est nettement plus bas que les autres (2 grands volumes + 2 satellites plutôt que 4 égaux) ; la neige est plus rare qu'en V0.5.1 (choix volontaire) ; le dessus reste en « pixels » de briques ; la forêt (18 arbres) est clairsemée et les 13 arbres décoratifs dominent car les terrasses 2×2 planes sont rares ; plage en dents de scie.
Rejeu : `bash run_all.sh`.
