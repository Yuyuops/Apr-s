# LEGO Maps — Option B : Premium constructible (V0.8, essai contrôlé)

Base technique : `research/lego-maps-v07-engine2-final`, Italie 64×96, note historique **15/25** (fidélité à la référence). `main` et moteur 1 inchangés.

## Choix produit
Faire un tableau LEGO élégant **avec de vraies pièces**, et non simuler une image parfaite nécessitant une couleur menthe inexistante, une pièce personnalisée, une fausse volute ou un coin concave non vérifié. La grille visible de 8 mm est une caractéristique esthétique assumée. N'introduire aucun faux tenon.

## Deux styles à comparer
- **Premium Ivoire / Or / Sauge** : cadre blanc, filet or et médaillons réels validés en V0.7, mer Sand Green (378) + Light Aqua (323), relief classique de 3 plaques par strate, plaque dorée.
- **Premium Noyer / Or / Lagon** : cadre Dark Brown (70), filet et médaillons or (297), mer Pale Blue (212) + Light Aqua (323), relief plus bas (2 plaques), compas décoratif existant, titre crème.

Ces configurations n'ajoutent **aucune famille de pièces** au catalogue; il faudra vérifier chaque association couleur×pièce dans les résultats. **Aqua 118 retiré des deux palettes** : pas de pavage partiel lié à son absence en 1×1. Aucune pièce de coin concave ajoutée.

Les fichiers sont dans `styles/premium_ivoire_or_sauge.json` et `styles/premium_noyer_or_lagon.json`.

## Barrières obligatoires
1. Générer les deux styles sur la même composition et grille 64×96.
2. Vérifier 0 collision, 0 déconnexion, 0 îlot perdu, 0 non-support, 0 substitution de couleur, 0 couple pièce/couleur non catalogué, 0 cellule de couleur de secours.
3. Rendre les vues **face et oblique à caméra et éclairage constants**, puis comparer à la V0.7. La note historique de fidélité 15/25 reste **intacte**.
4. Noter séparément la **qualité LEGO premium**, 5 critères /5 : lisibilité géographique, relief et hiérarchie, palette cohérente, cadre/typographie, harmonie générale. Notes explicitement justifiées par des images, jamais attribuées automatiquement par le script.
5. Critère de GO artistique : >=20/25 sur ce **nouveau référentiel déclaré avant notation**, 0 critère <3, et préférence réelle pour la variante face à V0.7. Cela ne signifie **pas** 20/25 de fidélité à l'image d'origine.
6. Contrôle d'achat distinct et obligatoire avant fabrication : stock actuel, prix unitaire, quantité suffisante, références substituables si nécessaire. **Présence dans les sets Rebrickable ≠ stock disponible.** Aucun achat automatique.
7. Après GO seulement, même style sur Écosse, Japon et Royaume-Uni, puis audit fragilité du moteur 1 (porteuses à un tenon / points d'articulation). Ne pas élargir sans preuve.

## Exécution
Workflow Actions isolé : `.github/workflows/lego-maps-premium-feasible.yml`.

Il génère et valide les deux variantes, puis archive leurs métriques et vrais rendus LDraw comme artefact. Si une variante échoue au moindre contrôle technique, le workflow échoue. Les scores artistiques et l'achat ne sont **pas** automatisés.

**État au commit de préparation :** configurations prêtes, exécution CI et validation artistique **non présumées**. Ne pas annoncer de GO avant inspection des preuves.
