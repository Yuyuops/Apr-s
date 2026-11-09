# Sprint V16 — Sélection des trois zones pilotes (32 × 32 tenons dans la variante B V15, grille 96 × 78)

Les zones sont découpées dans le raster de classes de B (`sprint_v15/data/hyrule_B_classes.npy`) : les fichiers de zone sont `zones/zone_{A,B,C}_classes.{tif,npy}` ; coordonnées (lignes, colonnes) du coin haut-gauche, nord en haut.

| Zone | Lignes | Colonnes | Position sur la carte | Composition (parts des classes) | Justification |
|---|---|---|---|---|---|
| **A — montagnes et falaises** | 0–32 | 56–88 | massif nord-est (volcan à cratère de la référence, repère mesuré en (0,74 ; 0,15) → ligne 12, colonne 71) | plateau brun 29,7 %, rouille 18,7 %, cratère 2,5 %, pierre 5,7 %, forêt 19,2 %, herbe 12,1 %, eau 6,8 %, hors-carte 3,8 % | contient le plus gros massif brun/rouille avec cratère, des falaises de plusieurs niveaux, la transition massif → forêt/herbe et un bout de mer : cas typique de l'« empilement de blocs » |
| **B — forêts et plaines** | 24–56 | 36–68 | centre (douves du château, repère (0,48 ; 0,36)) | herbe 54,8 %, forêt 17,3 %, lacs/rivières 6,4 %, eau (douves) 12,1 %, pierre 4,1 %, plateau brun 5,1 % | plaine centrale = « grandes surfaces vertes uniformes » du diagnostic ; forêts, rivières et douves permettent de tester végétation, sols et transitions |
| **C — eau et littoral** | 46–78 | 56–88 | sud-est (mer de la côte est, lacs du sud) | eau 24,0 %, herbe 29,6 %, forêt 25,0 %, pierre 16,4 %, neige 3,2 % | long littoral avec mer ouverte, rives herbeuses et rocheuses, bords de lacs ; contours géographiques à ne pas déformer |

Les trois zones sont disjointes ou presque (B et C se touchent sur les colonnes 56–68, lignes 46–56) et couvrent 9 des 12 classes. Le choix est fait **avant** tout essai, sur la seule composition de classes et les repères mesurés en V15.
