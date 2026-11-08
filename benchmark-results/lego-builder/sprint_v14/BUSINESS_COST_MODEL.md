# Sprint V14 — Modèle de coût et de rentabilité

> **Tous les prix, temps humains et purges ci-dessous sont des paramètres, pas des mesures.** Ceux marqués [V] viennent d'une page vérifiée le 2026-11-08 ; les autres sont des **hypothèses** à remplacer par des mesures (aucune imprimante n'a été achetée ni utilisée). Le classement final n'est retenu que s'il résiste à la plage bas/haut des hypothèses.

## Hypothèses
| Paramètre | Valeur | Statut |
|---|---|---|
| Prix A1 Combo | 469,95 € TTC | [V] LDLC |
| Prix Hi Combo | 474,90 € TTC (promos 359–370 non confirmées) | [V partiel] PcComponentes |
| Prix U1 | 699 € TTC (page « Unavailable ») | [V] Snapmaker EU |
| CFS supplémentaire (Hi) | 120 € TTC l'unité, 3 unités pour 16 couleurs | **hypothèse** : prix non vérifié |
| Filament | 18 € HT/kg (22 € TTC) | hypothèse (fourchette FR 15–30 € TTC [V]) |
| Électricité | 0.25 €/kWh, 150 W moyens | hypothèse (max 1 150 W [V] pour Hi/U1) |
| Main-d'œuvre | 25 €/h | hypothèse |
| Durée de vie machine | 4000 h, entretien 0.05 €/h | hypothèse |
| Capacité | 500 h/mois/machine | hypothèse (≈ 70 % d'utilisation) |
| Taux de refabrication | +10 % | hypothèse |
| Manutention | 4 min/plateau, 3 min/changement de bobine | hypothèse |
| Assemblage | 6 s/brique ; 40 s/pièce monochrome ; 15 min/module + 10 min dépose des supports | hypothèse |
| Purge par changement de couleur A1/Hi (bas–médian–haut) | 0,3 – 0,8 – 1,5 g | **hypothèse non vérifiée** (aucun chiffre constructeur) |
| Purge U1 | 0,045 – 0,12 – 0,225 g | affirmation constructeur « −85 % » [V page] appliquée à l'hypothèse ci-dessus : **non mesurée** |
| Durée d'un changement A1/Hi | 30 – 45 – 90 s | hypothèse |
| Durée d'un changement U1 | 5 – 5 – 10 s | [V] constructeur (5 s) ; non mesuré |
| TVA | 20 % ; coûts et marges en € HT |  |

## Faisabilité des procédés selon les emplacements couleur
| Procédé | A1 + AMS Lite (4) | Hi + CFS (4, extensible 16) | U1 (4 têtes) |
|---|---|---|---|
| Paco — 2 Modules multicolores | **impossible** (4/8 modules > 4 couleurs par couche) | possible avec 3 CFS supplémentaires | **impossible** (même limite) |
| Hyrule — 2 Modules multicolores | **impossible** (8/9 modules > 4 couleurs par couche) | possible avec 3 CFS supplémentaires | **impossible** (même limite) |
| 1 Briques / 3 Pièces monochromes | possible | possible | possible |

## Coût complet par modèle — Paco (scénario médian ; bas–haut pour les purges)

| Machine | Procédé | Faisable | Plateaux | Heures machine | Filament utile (g) | Supports (g) | Purge (g) | Changements | Matière € | Élec. € | Intervention (h) | Humain € | Amortissement € | **Coût complet € HT** | (bas – haut) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | briques | oui | 21 | 162 | 1948 | 0 | 0 | 0 | 39 | 7 | 6.8 | 171 | 26 | **242** | 242 – 242 |
| A1 | modules multicolores | **non** | 8 | 187 | 1084 | 680 | 6392 | 7990 | 162 | 8 | 5.1 | 127 | 30 | **326** | 240 – 457 |
| A1 | modules monochromes | oui | 7 | 128 | 1441 | 845 | 0 | 0 | 45 | 5 | 8.8 | 219 | 21 | **291** | 291 – 291 |
| Hi | briques | oui | 21 | 162 | 1948 | 0 | 0 | 0 | 39 | 7 | 6.8 | 171 | 26 | **242** | 242 – 242 |
| Hi | modules multicolores | oui | 8 | 187 | 1084 | 680 | 6392 | 7990 | 162 | 8 | 4.2 | 104 | 46 | **319** | 231 – 459 |
| Hi | modules monochromes | oui | 7 | 128 | 1441 | 845 | 0 | 0 | 45 | 5 | 8.8 | 219 | 21 | **291** | 291 – 291 |
| U1 | briques | oui | 21 | 162 | 1948 | 0 | 0 | 0 | 39 | 7 | 6.8 | 171 | 35 | **251** | 251 – 251 |
| U1 | modules multicolores | **non** | 8 | 98 | 1084 | 680 | 959 | 7990 | 54 | 4 | 5.1 | 127 | 21 | **206** | 194 – 225 |
| U1 | modules monochromes | oui | 7 | 128 | 1441 | 845 | 0 | 0 | 45 | 5 | 8.8 | 219 | 28 | **297** | 297 – 297 |

## Coût complet par modèle — Hyrule (scénario médian ; bas–haut pour les purges)

| Machine | Procédé | Faisable | Plateaux | Heures machine | Filament utile (g) | Supports (g) | Purge (g) | Changements | Matière € | Élec. € | Intervention (h) | Humain € | Amortissement € | **Coût complet € HT** | (bas – haut) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | briques | oui | 131 | 1207 | 13929 | 0 | 0 | 0 | 276 | 50 | 26.3 | 657 | 196 | **1179** | 1179 – 1179 |
| A1 | modules multicolores | **non** | 9 | 180 | 5450 | 69 | 3225 | 4031 | 173 | 7 | 4.6 | 115 | 29 | **325** | 282 – 391 |
| A1 | modules monochromes | oui | 43 | 208 | 6905 | 124 | 0 | 0 | 139 | 9 | 13.8 | 345 | 34 | **527** | 527 – 527 |
| Hi | briques | oui | 131 | 1208 | 13929 | 0 | 0 | 0 | 276 | 50 | 26.3 | 657 | 198 | **1180** | 1180 – 1180 |
| Hi | modules multicolores | oui | 9 | 180 | 5450 | 69 | 3225 | 4031 | 173 | 7 | 4.9 | 124 | 44 | **349** | 304 – 419 |
| Hi | modules monochromes | oui | 43 | 208 | 6905 | 124 | 0 | 0 | 139 | 9 | 13.8 | 345 | 34 | **527** | 527 – 527 |
| U1 | briques | oui | 131 | 1208 | 13929 | 0 | 0 | 0 | 276 | 50 | 26.3 | 657 | 260 | **1242** | 1242 – 1242 |
| U1 | modules multicolores | **non** | 9 | 135 | 5450 | 69 | 484 | 4031 | 119 | 6 | 4.6 | 115 | 29 | **268** | 262 – 278 |
| U1 | modules monochromes | oui | 43 | 208 | 6905 | 124 | 0 | 0 | 139 | 9 | 13.8 | 345 | 45 | **538** | 538 – 538 |

## Marge brute (prix TTC → HT) pour le procédé faisable le moins cher de chaque machine
**Les briques imprimées individuellement (procédé 1) sont exclues du classement** : 116 pièces Paco (3,6 %) et 515 pièces Hyrule (4,8 %) — pentes, quarts de rond, pièces spéciales — ne sont pas imprimables en briques rectangulaires, donc le modèle serait visuellement dégradé ; en outre l'emboîtement FDM n'est pas démontré.
(les prix de vente sont des **points de test**, pas une étude de marché)

### Paco
| Machine | Procédé retenu | Coût complet HT | Heures | Marge à 249 € TTC | Marge à 399 € TTC | Marge à 599 € TTC |
|---|---|---|---|---|---|---|
| A1 | modules monochromes | 291 € | 128 h | -83 € (-40 %) | 42 € (13 %) | 208 € (42 %) |
| Hi | modules monochromes | 291 € | 128 h | -83 € (-40 %) | 42 € (13 %) | 208 € (42 %) |
| U1 | modules monochromes | 297 € | 128 h | -90 € (-43 %) | 35 € (11 %) | 202 € (40 %) |

### Hyrule
| Machine | Procédé retenu | Coût complet HT | Heures | Marge à 399 € TTC | Marge à 699 € TTC | Marge à 999 € TTC |
|---|---|---|---|---|---|---|
| A1 | modules monochromes | 527 € | 208 h | -194 € (-58 %) | 56 € (10 %) | 306 € (37 %) |
| Hi | modules multicolores | 349 € | 180 h | -16 € (-5 %) | 234 € (40 %) | 484 € (58 %) |
| U1 | modules monochromes | 538 € | 208 h | -206 € (-62 %) | 44 € (8 %) | 294 € (35 %) |

## Scénarios mensuels (5 / 20 / 50 modèles vendus) — capacité machine 500 h/mois
(un « modèle vendu » = un Paco **ou** un Hyrule ; machines nécessaires = heures × (1+refabrication) / capacité)

| Produit | Machine | Procédé | N/mois | Heures requises | Machines nécessaires | Investissement HT | Marge brute mensuelle au prix médian | Retour sur investissement |
|---|---|---|---|---|---|---|---|---|
| paco | A1 | modules monochromes | 5 | 638 h | **2** | 783 € | 209 € | 2.5 mois |
| paco | A1 | modules monochromes | 20 | 2552 h | **6** | 2350 € | 836 € | 1.9 mois |
| paco | A1 | modules monochromes | 50 | 6380 h | **13** | 5091 € | 2090 € | 1.6 mois |
| paco | Hi | modules monochromes | 5 | 638 h | **2** | 792 € | 208 € | 2.5 mois |
| paco | Hi | modules monochromes | 20 | 2552 h | **6** | 2374 € | 832 € | 1.9 mois |
| paco | Hi | modules monochromes | 50 | 6380 h | **13** | 5145 € | 2080 € | 1.6 mois |
| paco | U1 | modules monochromes | 5 | 638 h | **2** | 1165 € | 176 € | 3.7 mois |
| paco | U1 | modules monochromes | 20 | 2552 h | **6** | 3495 € | 702 € | 2.8 mois |
| paco | U1 | modules monochromes | 50 | 6380 h | **13** | 7572 € | 1755 € | 2.4 mois |
| hyrule | A1 | modules monochromes | 5 | 1041 h | **3** | 1175 € | 278 € | 2.6 mois |
| hyrule | A1 | modules monochromes | 20 | 4164 h | **9** | 3525 € | 1110 € | 2.0 mois |
| hyrule | A1 | modules monochromes | 50 | 10410 h | **21** | 8224 € | 2775 € | 1.8 mois |
| hyrule | Hi | modules multicolores | 5 | 900 h | **2** | 1392 € | 1170 € | 1.0 mois |
| hyrule | Hi | modules multicolores | 20 | 3600 h | **8** | 5566 € | 4678 € | 1.0 mois |
| hyrule | Hi | modules multicolores | 50 | 9000 h | **18** | 12524 € | 11695 € | 0.9 mois |
| hyrule | U1 | modules monochromes | 5 | 1042 h | **3** | 1748 € | 222 € | 3.9 mois |
| hyrule | U1 | modules monochromes | 20 | 4166 h | **9** | 5242 € | 890 € | 2.9 mois |
| hyrule | U1 | modules monochromes | 50 | 10415 h | **21** | 12232 € | 2225 € | 2.7 mois |

**Seuil de rentabilité (retour de l'investissement machine en 12 mois au prix médian)** : N minimal par mois = investissement / (12 × (prix HT − coût variable)). Voir colonne « Retour sur investissement » : un retour ≤ 12 mois correspond à un seuil atteint.

## Limites
- Les coûts humains (assemblage de 3 193 à 10 682 briques ou de 400–600 pièces) dominent plusieurs procédés ; ils reposent sur des durées **supposées**.
- Les heures machine viennent d'un profil proxy lent : les vitesses réelles des firmwares sont inconnues, donc les capacités (machines nécessaires) peuvent être surestimées ou sous-estimées d'un facteur à mesurer.
- Aucune compatibilité d'emboîtement FDM n'est démontrée (coupon non imprimé) : un modèle assemblé à partir de briques imprimées n'est **pas** garanti de tenir.
