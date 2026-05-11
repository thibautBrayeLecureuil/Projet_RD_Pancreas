# PAOA (Pancréas artificiel openAPS)

## Présentation
Ce projet à pour but de mettre en place une interface entre le simulateur de patient T1DMS et l'algorithme Oref0.
Le code présent dans ce dépôt concerne uniquement l'interface développée en python.

## Installation rapide

> [!CAUTION]
> Avant d'installer ce projet, il vous faudra installer Oref0. Pour cela allez voir la [`documentation`](https://github.com/openaps/oref0) du projet Oref0. 

En executant la commande suivante, le projet va être téléchargé puis dézippé. L'interface se lancera directement sur le port 8081.

```curl -L -O https://raw.githubusercontent.com/thibautBrayeLecureuil/Projet_RD_Pancreas/main/init.sh && chmod +x init.sh && ./init.sh```

L'installation de la bibliothèque python Flask est faite par le script init.sh. Néanmoins, il est possible que d'autres bibliothèques utilisées par le projet ne soient pas installées sur votre poste. Vous devrez, dans le cas échéant, les installer manuellement.

> [!IMPORTANT]
> Si le port est déjà utilisé, l'interface ne pourra pas se lancer. Pour corriger cela, il vous faudra modifier la variable "port" dans le fichier "config.json"

## Architecture

### Ressources
Dans le dossier "ressources", vous trouverez tous les fichiers nécessaires à la configuration et au bon fonctionnement d'Oref0.

Les fichiers "pumphistory.json" et "glucose.json" n'ont pas besoin d'être modifier. En effet, leur contenu est réécrit à chaque lancement de simulation et lors de la simulation.

### SRC
Vous trouverez dans le dossier "src" le code de l'interface. 

Le fichier "main.py" contient les différentes routes de l'API qui font appel à dataTreatment.

Le fichier "dataTreatment.py" permet de traiter et mettre en forme les données. C'est aussi dans ce dernier que l'appel à l'algorithme Ore0 est fait.

### Web
Le dossier "web" contient les templates en html permettant d'afficher les données des fichiers JSON.

Dans l'état actuel des choses ce dernier ne contient que la page de configuration du profile patient.

## Lancement de l'interface

Pour lancer l'interface vous pouver exécuter la commande d'installation. Le script init.sh prend en charge la supression de l'ancien répertoire.

Vous pouvez aussi executer le fichier main.py avec la commande ```python3 [PATH]/main.py```

> [!IMPORTANT]
> Remplacez "PATH" par votre chemin d'accès.

## Configuration

Le fichier "config.json" contient la configuration du projet.

Vous y trouverez le port ainsi que la valeur de décalage temporel à chaque appel de l'interface.
