# Verdict V8.2 : **VALIDER AVEC LIMITATION**

**Ce que le diagnostic établit.** La différence de lisibilité du profil gauche **n'est pas** une occultation géométrique : la surface de cavité visible du LEGO est à 98 % de celle du GLB, et la joue cache la même part (31 % contre 29 %). **Ce n'est pas non plus un revêtement incomplet** : l'intérieur de la bouche du GLB est jaune à 97-100 %.

**Ce qui a été corrigé (une seule correction générique).**

- La **sélection de la cavité** passe de colonnes mélangeant les hauteurs à une composante 3D. Le revêtement de V8.1 touchait en réalité 130 cellules hors de la bouche (pieds, jambes et bassin) : défaut de V8.1, corrigé.
- La **ligne de lèvre sombre**, sans référence dans le GLB, est supprimée. Les couleurs de la cavité viennent du GLB.

**Limitations qui subsistent :**

- 79 % du sombre visible dans la zone de la bouche vu de gauche vient des pièces de la fixation de l'oreille basse (module gelé).
- Le liseré rouge de la langue (moins d'une cellule) n'est pas représentable.
- La bouche de V8.2 se lit moins nettement qu'en V8.1 sur le profil droit. L'avantage de V8.1 venait d'un trait absent de la référence.

**Les contrôles passent :** 0 collision, 0 pièce déconnectée, 326 étapes, 73 couples pièce × couleur vérifiés ; oreilles, yeux et truffe inchangés ; non-régression V6 / V6.1 sans différence. Les sous-ensembles sous 0,5 N passent de 49 (V8) à 50, avec un nouveau groupe loin de la bouche, justifié.

**Le personnage reste reconnaissable.** Pas de « BLOCAGE RÉEL » : la différence visuelle est locale (coin de la bouche gauche), sa cause est démontrée, et elle ne vient pas du moteur de détails.

**Règle d'arrêt : aucune nouvelle itération sur cette bouche sans décision.**
