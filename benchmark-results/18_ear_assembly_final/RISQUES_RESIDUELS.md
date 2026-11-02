# Risques résiduels : V9.1

| # | Risque | Gravité | Fondement | Que faire |
|---|---|---|---|---|
| 1 | **Aucun essai physique.** Ni la tenue des oreilles renforcées, ni le montage, ni la stabilité debout n'ont été vérifiés. | **Réserve de verdict** | Aucun achat ni essai autorisé | `PROTOCOLE_ESSAI_PHYSIQUE.md` |
| 2 | **Tuiles à cheval chargées en cisaillement.** Le poids d'une calotte de bord agit selon Y ; les tenons des tuiles sont orientés selon T. Le modèle de résistance (traction et moment, 1 N par tenon) ne sait pas compter le cisaillement : le gain mesuré (0,08 N → au moins 0,54 N pour les cas d'oreille) est celui du modèle, pas démontré. | **Élevée** | `RAPPORT_RESISTANCE.md` § 4 | Essai de traction sur les bords d'oreille de la sculpture montée |
| 3 | **Marge faible sur le seuil.** Deux petits cas d'oreille sont à 0,54 N (1,8 et 1,9 g, 2 tenons), 0,62 et 0,81 N pour d'autres : au-dessus de 0,5 N, mais de peu. Le seuil de 0,5 N est un critère de manipulation fixé en V7, pas une propriété du matériau. | Moyenne | `validation/oreilles_9_cas_les_plus_faibles_V91.json` | Essai de manipulation ; si l'on exige une marge, renforcer à nouveau (autres joints de plaques, tuiles 2×2) |
| 4 | **Quatre groupes fragiles non renforcés** : bout du museau (0,19 N, 1,3 g), museau (0,26 N, 1,4 g), main gauche (0,26 N, 1,0 g), **main droite (0,26 N, 2,1 g, manipulable)**. Doigts et museau d'une cellule de large : ni cellule cachée, ni joint de plaques à décaler sans modifier la forme. | Moyenne (main droite) / faible (autres) | `RAPPORT_RESISTANCE.md` § 5 ; page 2 de la notice | Hors périmètre de cette mission ; à décider : plaque traversante dans l'avant-bras, ou accepter |
| 5 | **55 poses de bras à tenir à la main** (bras en construction instable) ; **57 poses de l'oreille basse par le dessous** (tenir l'oreille en l'air ou la retourner) ; **8 premières étapes de l'oreille basse** instables à plat. | Moyenne (usage) | `RAPPORT_NOTICE.md` §§ 2-3 | Essai de montage ; étudier le montage à plat des bras et l'ordre de l'oreille basse |
| 6 | **Le séquenceur et le rejeu ne modélisent que des translations rigides** (avec dégagement de 5 ldu puis glissement) : pas de rotation en cours de pose, pas de doigts, pas de souplesse des pièces, tenons et creux hors du modèle de collision, pièces pleines assimilées à des boîtes. Les deux modèles de collision sont indépendants, mais pas indépendants du principe du « solide rigide ». | Moyenne | `RAPPORT_31_PIECES.md` §§ 4-5 | Essai de montage par une personne |
| 7 | **Notice non suivie par un monteur.** Les contrôles sont numériques. | Moyenne | | Essai de montage |
| 8 | **Masse réelle inconnue.** Le modèle (0,10 g par case) est calibré sur des briques ; la sculpture, faite de plaques, est probablement plus lourde. Les poids et les marges de gravité réels en dépendent. | Moyenne | `RAPPORT_V91.md` § 4 | Peser la sculpture et les pièces |
| 9 | **Dérive du moteur de volume** de V8 à V8.2 (21 cellules de surface aux épaules), signalée et non corrigée, héritée de V9. | Faible | V9 | Éviter la reconstruction globale pour les modifications locales (V9 et V9.1 le respectent) |
| 10 | **Tracé des joints de tuiles de l'oreille basse modifié** (18 tuiles à cheval) : même couleur, même surface, 0,05 à 0,12 % des pixels. | Faible (esthétique) | `comparaisons/` | Aucune |
| 11 | **Indépendance mécanique des deux chemins de fixation** non recalculée en V9.1 : héritée de V7 (pièces identiques). Les bancs d'essai de V7 restent valables. | Faible | `validation/checks_v91.json` | Banc d'essai de fixation |
| 12 | **Erreur de V9 corrigée par V9.1** : l'affirmation « 31 pièces sans séquence » et le verdict CORRIGER de V9 reposaient sur une limite de l'outil. Si d'autres verdicts de V9 reposent sur ce même planificateur (accessibilité du corps, des bras), ils ont été **rejoués avec le nouveau séquenceur seulement pour les oreilles** ; le corps et les bras gardent le contrôle de V9. | Faible | `RAPPORT_31_PIECES.md` | Rejouer le corps et les bras avec `seq.py` si l'on veut la même exigence |

## Ce qui est démontré dans les limites du modèle

* Les 337 pièces d'oreille de V9 et les 181 + 188 de V9.1 ont une séquence de montage, chacune par un mouvement rigide dont le chemin est libre, vérifié par deux modèles de collision.
* Aucune collision, aucune pièce déconnectée, aucun îlot, aucun tenon bloqué dans le modèle complet.
* Le contrôle de portée détecte les changements non autorisés (16 tests).
* La géométrie V6.1 des oreilles est inchangée (rejeu AUCUNE DIFFERENCE).
