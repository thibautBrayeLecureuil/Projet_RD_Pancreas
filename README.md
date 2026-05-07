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

###Ressources
Dans le dossier "ressources", vous trouverez tous les fichiers nécessaire à la configuration et au bon fonctionnement d'Oref0.

### SRC
Vous trouverez dans "src" le code de l'interface. 

Le fichier "main.py" contient les différentes routes de l'API et fait apppel à dataTreatment.

Le fichier "dataTreatment.py" permet de traiter et mettre en forme les données. C'est aussi dans ce dernier que l'appel à l'algorithme Ore0 est fait.

### Web
Le dossier "web" contient le code html permettant d'afficher les données des fichiers JSON.

Dans l'état actuel des choses ce dernier ne contient que la page de configuration du profile du patient.

