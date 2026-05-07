echo "====================================="
echo " --- Recupération du projet PAOA --- "
echo "====================================="

rm -rf Interface
wget https://github.com/thibautBrayeLecureuil/Projet_RD_Pancreas/archive/refs/heads/main.zip
unzip main
mv Projet_RD_Pancreas-main/ Interface/
rm main.zip

echo "====================================="
echo " - Installation Flask + dépendances -"
echo "====================================="

# Vérifie que Python3 est installé
if ! command -v python3 &> /dev/null
then
    echo "Python3 n'est pas installé."
    exit 1
fi

# Vérifie que pip est installé
if ! command -v pip3 &> /dev/null
then
    echo "pip3 n'est pas installé."
    exit 1
fi

pip install flask

echo "====================================="
echo " ---- Lancement de l'interface ---- "
echo "====================================="

cd Interface
python3 ./src/main.py
