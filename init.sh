rm -rf Interface
wget https://github.com/thibautBrayeLecureuil/Projet_RD_Pancreas/archive/refs/heads/main.zip
unzip main
mv Projet_RD_Pancreas-main/ Interface/
rm main.zip
cd Interface
python3 main.py
