# Sprint V17 — Audit de la référence (Rebrickable MOC-193441)

## 1. Ce que j'ai pu vérifier, et comment
| Source | Accès | Résultat |
|---|---|---|
| `https://rebrickable.com/mocs/MOC-193441/` (curl) | **HTTP 403**, page Cloudflare « Just a moment… » (défi anti-robot) | non contourné |
| même URL, outil de lecture web | **HTTP 402 Payment Required** | non contourné ; aucun achat |
| Moteur de recherche | résultat : *LEGO MOC-193441 Hyrule—The Legend of Zelda: Breath of the Wild* par **Galaxy333**, ≈ 14 876 pièces, instructions PDF **payantes (40 $, MOC premium)**, éléments cités : tours Sheikah, étables, Bêtes divines, dragons | vérifié **indirectement** (résumé du moteur, page non lue) |
| Fiches de revendeurs tiers (MOC Brick Store A1622 « MOC-193441 The Legend of Zelda: Breath of the Wild », ≈ 14 841 pièces, ≈ 81,6 × 81,6 cm ; YWOBB) | pages publiques lues | 3 images produit récupérées (analyse privée) |

**Le MOC correspond-il à la photographie jointe ?** Oui, avec une confiance élevée mais **sans lecture directe de la page Rebrickable** : la photographie que vous avez jointe et deux des trois images des fiches revendeurs sont le même rendu numérique (même cadrage trois-quarts, même carte : plateau des Pionniers neigeux au nord-ouest, volcan au nord-est, désert au sud-ouest, bandeau noir « THE LEGEND OF ZELDA BREATH OF THE WILD », ornements Sheikah aux coins). La fiche revendeur nomme explicitement MOC-193441.

## 2. Photographies complémentaires réellement disponibles
| Vue demandée | Disponible ? |
|---|---|
| Dessus | **oui, 1** (fiche revendeur, 750 × 1000 px, carte ≈ 540 px de large) |
| Trois-quarts | **oui, 3** (votre photo 933 × 800 + 2 images de revendeur) |
| Latérale | **non** |
| Gros plans de bâtiments | **non** (le château fait ≈ 25 px de large sur la vue de dessus) |
| Gros plans de ponts / végétation | **non** |
Conséquence : les **hauteurs et profils des objets ne sont pas mesurables** ; seules les positions en plan et les ordres de grandeur le sont. Voir `MULTIVIEW_ANALYSIS.md`.

## 3. Fichiers 3D / instructions
- **Instructions PDF : payantes** (40 $) → **non achetées, non consultées**.
- **Fichier Stud.io / LDraw / .io / liste de pièces XML-CSV** : **aucune preuve d'accès légal gratuit**. Une fiche revendeur dit se fonder sur « le fichier CSV de Rebrickable » (liste de pièces, non accessible). Rien n'a été supposé : **aucun modèle 3D de la référence n'est utilisé**.

## 4. Usage des images
Les images tierces ne servent qu'à une analyse privée et à des **planches comparatives** (recadrages réduits) dans `renders/` ; elles ne sont pas redistribuées en entier. Si vous préférez, ces planches peuvent être régénérées sans les recadrages de la référence.
