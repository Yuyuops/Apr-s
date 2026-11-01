# Verdict V7 : **INTÉGRATION PARTIELLE**

**Ce qui marche.** La première sculpture complète de Paco (400 mm) est produite **automatiquement** de bout en bout, sans aucune pièce placée à la main. La chaîne :

1. grille complète ;
2. segmentation ;
3. deux oreilles V6.1, avec fixation 3-4-5 à deux chemins et plaque secondaire cachée ;
4. volume brickify_plus ;
5. appuis ;
6. notice.

Le modèle de 2 773 pièces passe `validate_v3` :

- 0 collision ;
- 0 pièce déconnectée ;
- 331 étapes réalisables ;
- 68 couples pièce × couleur vérifiés ;
- centre de gravité dans l'appui.

Le personnage est reconnaissable sous toutes les vues.

**Pourquoi « partielle » :**

- **capacité manquante** pour les petits détails du visage (yeux, truffe, bouche) ;
- mains fragiles ;
- notice des oreilles non détaillée ;
- seuil de segmentation réglé au vu de ce cas.

**Pourquoi pas « architecture à corriger ».** Tout s'est intégré par des adaptateurs génériques, sans aucun traitement propre à Paco.

**Prochaine étape conseillée (non commencée) :** module de détails ronds de surface, puis essai physique des deux bancs (sur autorisation).
