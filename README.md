# Après

**Après** est un moteur open source de simulation de politiques publiques. Il transforme des propositions politiques sourcées en mesures structurées, puis estime leurs effets dans le temps en séparant faits, calculs, hypothèses et scénarios.

## MVP

Le premier jalon est un banc d'essai du **Policy Compiler** :

1. ingérer des programmes officiels et versionnés ;
2. atomiser les propositions en `Policy Objects` ;
3. classifier action, cible, calendrier, prérequis et domaines touchés ;
4. distinguer effets **calculables**, **modélisables** et **scénarisables** ;
5. produire un audit de couverture ;
6. refuser d'inventer une conséquence quand les données ou hypothèses manquent.

## Principes

- même méthode pour tous les partis et programmes ;
- source primaire + version obligatoires ;
- traçabilité de chaque résultat jusqu'à la source, la règle et l'hypothèse ;
- incertitude explicite et croissante avec l'horizon temporel ;
- aucune opinion politique générée par le moteur ;
- un objectif politique n'est pas automatiquement une mesure exécutable.

## Démarrage

```bash
python -m pip install -e ".[dev]"
python audit_programs.py
pytest
```

Le front web viendra après validation de la couverture du moteur.


## Démo web locale

Le MVP web fonctionne sans backend ni clé API :

```bash
python -m http.server 8000 -d web
```

Puis ouvrir `http://localhost:8000`.

La démo permet de saisir une mesure, choisir un horizon de 1 à 60 mois et visualiser :
- les effets comptables directement calculables ;
- les capacités de modélisation encore manquantes ;
- les réformes qui nécessitent des scénarios plutôt qu'un chiffre unique ;
- les hypothèses utilisées.

Les mesures synthétiques sont explicitement marquées comme telles. Une mesure attribuée à une organisation doit conserver sa source et son statut temporel.
