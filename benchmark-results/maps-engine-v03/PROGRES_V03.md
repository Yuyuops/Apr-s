# Etat intermediaire V0.3 (pas encore un verdict)

- Quatre references V0.2 ont ete inspectees dans le depot, sans modification.
- Ecosse 32x32 : 301 pieces, 44 porteuses faibles, 17 porteuses critiques.
- Ecosse 48x48 : 487 pieces, 44 faibles, 19 critiques.
- Test local de voisinage depuis les tableaux de pieces archives : 8 critiques / 17 en 32x32 et 5 / 19 en 48x48 n'ont aucune plaque reguliere voisine de meme couleur et region. Elles ne se resoudront pas par fusion simple.
- 26 blobs V0.2 copies vers un nouveau repertoire V0.3, archive d'origine intacte.
- Optimiseur exact local implemente, respecte la geometrie et les couleurs; tests unitaires et script d'execution ajoutes.
- Carte de test original d'archipel ajoutee, pour un cinquieme cas.

NON VERIFIE : execution du moteur V0.3 sur les cinq cartes, reduction effective des critiques, rendus et notices regeneres, validation physique. Ces resultats exigent un runner possedant LDraw, Rebrickable, Git LFS, Node et les dependances verrouillees.

La recherche est limitee aux paires/trios et 32 cellules maximum. Les cas non resolus seront diagnostiques, pas declares impossibles par principe. Ne pas baisser les seuils.
