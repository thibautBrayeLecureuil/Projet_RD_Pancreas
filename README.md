# Projet_RD_Pancreas

## Présentation
Ce projet à pour but de mettre en place une interface entre le simulateur de patient T1DMS et l'algorithme Oref0.
Le code présent dans ce dépôt concerne uniquement l'interface développée en python.

## Installation rapide

> [!CAUTION]
> Avant d'installer ce projet, il vous faudra installer Oref0. Pour cela allez voir la [`documentation`](https://github.com/openaps/oref0) du projet Oref0. 

En executant la commande suivante, le projet va être téléchargé puis dézippé. L'interface se lancera directement sur le port 8081.

```curl -L -O https://raw.githubusercontent.com/thibautBrayeLecureuil/Projet_RD_Pancreas/main/init.sh && chmod +x init.sh && ./init.sh```

> [!IMPORTANT]
> Si le port est déjà utilisé, l'interface ne pourra pas se lancer. Pour corriger cela, il vous faudra modifier la variable "PORT" dans le fichier "/src/main.py"

## Architecture

Dans le dossier "ressources", vous trouverez tous les fichiers nécessaire à la configuration et au bon fonctionnement d'Oref0.
