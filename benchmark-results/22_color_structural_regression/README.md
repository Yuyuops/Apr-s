# V12.1 — fidélité des couleurs sans régression mécanique

Point de départ : V12 (commit dcadff5). Gains colorimétriques de V12 validés et conservés ; correction ciblée des régressions mécaniques, sans nouvelle optimisation esthétique. Aucun seuil de validateur, aucun coefficient de tenue, aucun GLB, aucune archive précédente n'a été modifié.

Lire dans l'ordre : `VERDICT.md` · `RAPPORT_CAUSE_RACINE.md` · `COMPARAISON_MECANIQUE.md` · `AUDIT_NOTICES.md` · `AUDIT_OREILLE_HAUTE.md`.

Contenu : `modeles/` (Beagle V12.1 ; Paco option A = palette V12, option B = palette V11 + réparation ; brut, notice plate, nomenclature/catalogue, validation, groupes fragiles, journaux de renfort, contrôles de fixation d'oreille, périmètre) · `comparaison_mecanique/` (V11 / V12 / V12.1, JSON) · `audit_couleurs/` (audit de fidélité et cartes de défauts des trois modèles) · `audit_oreille_haute/` (mesures des deux oreilles, trois jeux de modèles) · `rendus/` (GLB / V11 / V12 / V12.1, vues d'ensemble, crâne, oreille haute) · `notices/` (plans hiérarchiques) · `journaux/` (rejeu complet depuis le moteur portable : journal et manifeste de chaque exécution) · `tests/` (résultats : 18/18).

Moteur (`../20_portable_engine/engine/`) : `reinforce.py` (plafond de groupe paramétrable, pont raccourci, pavages alternatifs ; comportement historique par défaut), `lego_run.py` (paramètres `max_group_parts`, `shorten_on_cut`, étape optionnelle `notice`), `mech_compare.py`, `exposed_diff.py`, `ear_diagnosis.py` (nouveaux). Sujets : `subjects/beagle.json` et `subjects/paco.json` (V12.1), `subjects/paco_option_B.json`, `subjects/*_fixed_v11.json` (génération historique).
Rejeu : `LEGO_DEPS=<deps avec la base rb.db de référence> python engine/lego_run.py --glb <glb> --subject subjects/<sujet>.json --out <dossier>` ; deux rejeux successifs du Beagle et de l'option B sont identiques octet pour octet.
