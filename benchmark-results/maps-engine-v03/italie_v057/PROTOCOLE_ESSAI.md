# Protocole d'essai physique à préparer (non exécuté — aucune validation physique n'est revendiquée)
Objectif : mesurer les jonctions les plus chargées et le futur système d'accrochage, à partir du modèle numérique V0.5.6.
1. **Pièces à construire** : (a) secteur S11 (Toscane, 32×32, ≈ 720 pièces) avec une base 8×8 en deux couches décalées ; (b) un tronçon de 8 tenons de façade du Colisée (arches 6182 + fenêtres 60592) sur plaza ; (c) une pente 75° (4460a/3684a) empilée sur 3 briques ; (d) un conifère 3941+3942c ; (e) une jonction inter-secteurs (joint des plaques de base).
2. **Essais** : traction axiale sur 10 pièces à un tenon portant (briques 1×1 de crêtes, piliers de façade) jusqu'à rupture de maintien — comparer au 1 N/tenon supposé par le validateur ; flexion 3 points d'un secteur 32×32 sur appuis de 8 tenons ; cisaillement de la jonction inter-secteurs ; chute de 30 cm d'un secteur de 1,4 kg dans sa boîte de transport.
3. **Accrochage** : le tableau complet pèse ≈ 10,4 kg (±30 %). Prévoir un fond rigide indépendant (panneau + équerres) ; essai de charge statique ×3 pendant 7 jours sur un module 32×32 monté verticalement ; mesure de flèche au centre.
4. **Critères** : aucune pièce détachée après 3 manipulations, flèche < 2 mm sur 32 tenons, rupture de maintien ≥ 2× la charge de service par tenon. Les seuils du validateur numérique ne sont pas modifiés.
5. **Jonctions les plus chargées d'après le graphe** : points d'articulation du socle/mer, plaza du Colisée, base de la Tour de Pise (pire perte isolée : 9 pièces, 10 g), briques 1×N de crêtes alpines.

## Ajout V0.5.7 : fichiers prêts
- `results/essai_secteur_S11/` : diorama.ldr, parts.json, parts_list.csv, bom_verification.csv, fragility.json (S11 + 8 tenons de jonction S12/S21, 1 576 pièces) : à construire pour les essais 1 à 3 ci-dessus.
- Les jonctions inter-secteurs à tester sont listées dans `results/E_italie/it57_b2/assembly_plan_v2.json` (`inter_sector_pieces`). Critère additionnel : après démontage en 2 modules, la jonction doit se remonter sans jeu visible.
- Aucun achat de pièces n'a été fait ; la liste d'achat n'est pas produite (stock/prix non vérifiés).
