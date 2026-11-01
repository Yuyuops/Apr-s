# Verdict V8 : **CORRIGER**

**Ce qui marche.** Le générateur fonctionne et produit automatiquement des détails en vraies pièces, à partir du GLB et de règles génériques :

- deux yeux (coupole 3×3 blanche + pupille ronde 1×1 noire, encastrés à la surface du GLB) ;
- une truffe (coupole 3×3 noire) ;
- une tuile de langue.

Le troisième œil du GLB, un artefact de génération, est détecté et écarté. Le regard est nettement plus fidèle qu'en V7.

**Les contrôles passent :**

- `validate_v3` : 0 collision, 0 pièce déconnectée, 331 étapes, 72 couples pièce × couleur vérifiés ;
- oreilles V6.1 identiques à V7 ;
- non-régression V6 / V6.1 : aucune différence (modèles, rapports, validations, nomenclatures).

**Le défaut qui empêche « VALIDER V8 » : la bouche.** Elle n'est pas plus lisible qu'en V7. Les surfaces tournées vers le bas et les traits n'ont pas encore de module de pièces.

**Correction minimale :** un module « ligne et cavité », décrit dans `PROBLEMES_NON_RESOLUS.md`, n° 1.

**Réserves secondaires :**

- truffe inclinée à 37° de son axe de pose ;
- œil gauche décalé de 7,6 mm ;
- trois règles réglées au vu de ce cas ;
- deux nouveaux petits groupes faibles.

**Pourquoi pas « REVOIR LA MÉTHODE ».** Aucun détail n'a été conçu à la main, et aucune coordonnée ni référence de pièce n'a été saisie pour Paco.
