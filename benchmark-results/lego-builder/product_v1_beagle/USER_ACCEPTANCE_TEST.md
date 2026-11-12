# Product V1 Beagle — Test d'acceptation utilisateur (parcours client)

Persona : une personne qui achète le Beagle, télécharge le ZIP et veut le construire. La partie automatisable est **exécutée** sur le ZIP seul, extrait dans un dossier vierge (`tools/simulate_customer_v1.py`, journal `validation/customer_simulation.json`). Les parties physiques restent **HUMAINES, non faites**.

| # | Étape du parcours | Test | Résultat |
|---|---|---|---|
| 1 | Télécharger le ZIP | copie dans « Downloads », test d'intégrité, extraction (24,4 Mo, 29 fichiers) | **PASS** |
| 2 | Ouvrir le guide | README + guide : 100 % des fichiers cités existent, aucun lien mort | **PASS** (la clarté pour un lecteur reste à confirmer par une personne) |
| 3 | Consulter les rendus | 7 PNG 2400 x 2400 décodables, non vides ; GIF de 12 images | **PASS** |
| 4 | Identifier les pièces | BOM ouverte comme un tableur : 64 lignes, total 10 567 ; import Rebrickable au bon format (Part, Color, Quantity) ; 12 références rares ou peu courantes signalées | **PASS** |
| 5 | Préparer les pièces | sacs par couleur : Dark Orange 6 263 (17 réf.), Dark Tan 1 704 (14), White 1 575 (16), Reddish Brown 775 (9), Black 250 (8) | tri **automatique PASS** ; tri physique **HUMAIN REQUIS** |
| 6 | Suivre la notice | montage virtuel des 554 étapes dans l'ordre contre le stock de la BOM : aucune pièce hors stock, sous-ensembles construits avant d'être fixés, max 20 pièces par étape | **PASS** numérique ; construction réelle **HUMAIN REQUIS** |
| 7 | Terminer le modèle | stock final = 0, 10 567 pièces posées, page finale présente | **PASS** numérique ; modèle réel **non construit** |

## Points bloquants / à risque identifiés
1. **Aucune construction réelle** : le parcours physique n'est PAS déclaré réussi.
2. **147 étapes à emboîter par en dessous** (dont 4 à 8) : probable difficulté, notice non testée par un constructeur.
3. **Étape 447** : insertion « de l'avant vers l'arrière du chien » (museau).
4. **Pièces** : plaque 4 x 6 Dark Orange x945 (21 sets Rebrickable) ; Dark Orange = 6 263 pièces ; disponibilité réelle et coût **non vérifiés**.
5. **Fragilité** : 47 % des liaisons à un seul tenon ; manipulation délicate avant la fin (voir limites).
6. Notice en français, noms de pièces en anglais.
7. Aucune personne extérieure n'a lu les fichiers : « GO utilisateur » non confirmé.

## Fiche de validation humaine
`docs/FICHE_VALIDATION_HUMAINE.md` dans le kit : à remplir par un testeur réel (14 questions : compréhension, pièces manquantes, étapes ambiguës ou impossibles, étapes par en dessous, solidité, temps, ressemblance).
