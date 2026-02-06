import json
import subprocess
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DES CHEMINS ---
# Cette partie permet au code de trouver le dossier 'ressources' automatiquement
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESSOURCES_DIR = os.path.join(BASE_DIR, '../ressources')

# Chemins absolus vers les fichiers JSON
GLUCOSE_FILE = os.path.join(RESSOURCES_DIR, "glucose.json")
IOB_FILE = os.path.join(RESSOURCES_DIR, "iob.json")
PROFILE_FILE = os.path.join(RESSOURCES_DIR, "profile.json")
TEMP_BASAL_FILE = os.path.join(RESSOURCES_DIR, "temp_basal.json")

def process(data_entree):
    # --- 2. EXTRACTION DE LA GLYCÉMIE ---
    valeur_glucose = 150 # Valeur de sécurité par défaut
    
    try:
        # On regarde si c'est un dictionnaire direct : {"glucose": 180}
        if isinstance(data_entree, dict) and 'glucose' in data_entree:
            valeur_glucose = int(data_entree['glucose'])
        # On regarde si c'est une liste : [{"glucose": 180}]
        elif isinstance(data_entree, list) and len(data_entree) > 0:
            if 'glucose' in data_entree[0]:
                valeur_glucose = int(data_entree[0]['glucose'])
        # On regarde si c'est un nombre direct
        elif isinstance(data_entree, int) or isinstance(data_entree, float):
             valeur_glucose = int(data_entree)
             
    except Exception as e:
        print(f"[Erreur Lecture Donnée] {e}")

    print(f"[OpenAPS] Calcul pour glycémie : {valeur_glucose} mg/dL")

    # --- 3. CRÉATION DE L'HISTORIQUE (Obligatoire pour OpenAPS) ---
    entries = []
    now = datetime.now()
    for i in range(3):
        t = now - timedelta(minutes=5*i)
        entries.append({
            "date": int(t.timestamp() * 1000),
            "dateString": t.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "sgv": valeur_glucose,
            "trend": 4, "device": "flask", "type": "sgv"
        })

    try:
        with open(GLUCOSE_FILE, 'w') as f:
            json.dump(entries, f, indent=4)
    except:
        print("Erreur d'écriture du fichier glucose.json")

    # --- 4. EXÉCUTION D'OPENAPS ---
    # On utilise les chemins absolus définis plus haut
    cmd = ['oref0-determine-basal', IOB_FILE, TEMP_BASAL_FILE, GLUCOSE_FILE, PROFILE_FILE]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True).stdout
        
        # --- 5. LECTURE DU RÉSULTAT ---
        dose = 0
        if result:
            for line in result.split('\n'):
                if 'rate' in line:
                    try:
                        d = json.loads(line)
                        if 'rate' in d:
                            dose = d['rate']
                            break
                    except: continue
        return dose
        
    except Exception as e:
        print(f"Erreur System OpenAPS: {e}")
        return 0