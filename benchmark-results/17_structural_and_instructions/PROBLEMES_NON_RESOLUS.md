# Problèmes non résolus : V9

| # | Problème | Gravité | Cause démontrée | Correction minimale (non engagée) |
|---|---|---|---|---|
| 1 | **31 pièces d'oreille sans séquence d'assemblage trouvée** (19 oreille basse, 12 haute) | **Empêche la validation** | Un noyau de pièces dont les liaisons s'exercent des deux côtés d'un même plan : aucune unité n'en sort par une translation rigide | Dans le générateur d'oreille (V6.1) : interdire les pièces emboîtées des deux côtés avant que leurs voisines ne soient posées, ou ajouter la séquence d'assemblage aux contraintes de choix. Ou faire juger ces 31 pièces par un essai de montage (protocole) |
| 2 | **4 groupes de bord d'oreille non renforcés**, dont 2 à **risque élevé** (15 pièces 5,1 g, 1 tenon 0,08 N ; 7 pièces 3,5 g, 1 tenon 0,21 N) | Empêche la validation (critère « structurels et manipulables renforcés ») | Pièces du module d'oreille (gelé) ; le renfort utilise le réseau de 20 × 8 × 20 LDU, et les oreilles sont tournées de 53° | Étendre R2 aux plans des oreilles (réseau tourné) ; ou exiger au moins 3 tenons par groupe de bord au générateur |
| 3 | Mains (2 groupes, 5 et 12 pièces, 0,26 N) | Moyen | Doigts d'une cellule de large : aucune cellule cachée autour | Plaque traversante dans l'avant-bras vers la paume (module de main), ou accepter comme décoration |
| 4 | Bout du museau (2 groupes, 7 et 9 pièces, 0,19 et 0,26 N) | Faible | Même cause (museau fin) | Idem |
| 5 | Dérive du moteur de volume : 21 cellules de surface ont changé de couleur à la hauteur des épaules entre V8 et V8.2 | Faible | Reconstruction globale par `brickify_plus` après une modification locale ; les entrées étaient identiques hors de la bouche | Éviter la reconstruction globale pour les modifications locales (comme le fait V9) ; non corrigé pour V8.2 |
| 6 | Pièces posées par le bas (338 pièces « suspendues ») | Moyen (usage) | Surplombs du volume (museau, oreilles, bras) sans rien dessous | Les pièces sont emboîtées par le bas après la pièce qui les tient : signalé page par page ; demande de tenir le modèle |
| 7 | +310 petites plaques (+11 %) par rapport à V8.2 | Faible | Recoupage des régions renforcées | — |
| 8 | Aucune validation physique ; modèle de résistance indicatif | — | Aucun achat autorisé | Protocole d'essai (`PROTOCOLE_ESSAI_PHYSIQUE.md`) |
| 9 | Planificateur limité (translations rigides, 4 LDU de jeu, pas de doigts) | Moyen | Voir `RAPPORT_NOTICE.md` § 4 | Essai de montage par une personne |
| 10 | Notice non suivie par un monteur | Moyen | — | Essai de montage |

**Corrigé dans cette itération (voir `RAPPORT_V9.md`) :**

- plan d'appui de la statue (4 plaques isolées, marge de 4,2 mm, pas de 74 mm comme annoncé en V7) ;
- 12 des 21 groupes fragiles de V8.2 ;
- contrôle de portée des modifications.
