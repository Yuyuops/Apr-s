# Hypothèses et cas du moteur Après

Ce registre transforme les hypothèses identifiées pendant la conception en exigences explicites du moteur.

## Principes

- une mesure peut produire un effet **calculable**, **modélisable**, **scénarisable** ou **non supporté** ;
- aucun effet secondaire chiffré n'est généré sans modèle, règle ou hypothèse explicitement enregistrée ;
- les réformes structurelles peuvent modifier le graphe institutionnel avant de modifier le graphe socio-économique ;
- un programme est simulé comme un paquet de mesures avec interactions, pas comme une simple somme indépendante ;
- l'incertitude augmente avec l'horizon.

## Horizons

- 1 mois : effets comptables directs et calendrier d'application ;
- 6 mois : mise en œuvre initiale et effets comportementaux uniquement si un modèle existe ;
- 1 an : effets budgétaires annuels, microsimulation fiscale-sociale, premiers effets macro si disponibles ;
- 2 ans : interactions, capacités des services publics, effets sectoriels ;
- 5 ans : effets structurels, boucles de rétroaction et scénarios bas/central/haut.

## Cas encodés

Le registre couvre notamment : SMIC, retraites, fiscalité, dépenses publiques, prestations sociales, santé, éducation, justice, police/sécurité, immigration/asile, logement, médias, environnement, énergie, transports/infrastructures, services publics, défense, numérique, nationalisation/privatisation, réforme constitutionnelle, réorganisation administrative, suppression d'une couche administrative, règles européennes/Schengen, sortie de l'UE, changement de régime monétaire/sortie de l'euro, sortie de l'OTAN et politique étrangère.

## Interactions encodées

Les interactions explicites incluent notamment :

- fiscalité + dépenses ;
- SMIC + cotisations/prélèvements ;
- sortie UE + régime monétaire ;
- réorganisation administrative + transfert de compétences ;
- énergie + fiscalité ;
- immigration + travail/logement ;
- nationalisation/privatisation + finances publiques/secteur ;
- retraites + emploi/prélèvements ;
- services publics + budget ;
- réforme constitutionnelle + architecture institutionnelle.

## Variables exogènes

Les modèles doivent pouvoir distinguer les effets du programme des chocs externes : taux BCE, croissance mondiale, pétrole, gaz, EUR/USD, démographie, commerce mondial et contexte UE.

Le fichier canonique est `data/hypotheses_registry.json`. La CI exécute `audit_hypotheses.py` afin d'empêcher l'ajout d'une nouvelle catégorie de mesure dans le compilateur sans cas méthodologique correspondant.
