import subprocess
import datetime
import json
import os

PATH = os.path.dirname(os.path.abspath(__file__))[:-4]

PATH_RESSOURCES = "./ressources"
IOB_FILE = PATH_RESSOURCES + "/iob.json"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
PROFILE_FILE = PATH_RESSOURCES + "/profile.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"
PUMP_HISTORY_FILE = PATH_RESSOURCES + "/pumphistory.json"
CURRENTTEMP_FILE = PATH_RESSOURCES + "/currenttemp.json"
MEAL_FILE = PATH_RESSOURCES + "/meal.json"
BASAL_FILE = PATH_RESSOURCES + "/basalprofile.json"

def process(data):

    with open(CLOCK_FILE, "r") as f:
        date = json.loads(f.read())
        
    date = (datetime.datetime.fromisoformat(date[:-1]) + datetime.timedelta(seconds=5)).isoformat() + "Z"

    glucose_data = {
        "date": date,
        "sgv": data,
        "direction": "Flat",
        "noise": 1
    }

    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())
        f.close()
        
    glucose_file.append(glucose_data)
   
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)
        f.close()

    return callLoop()

def callLoop():
    # 1. Mise à jour du fichier basalprofile
    with open(PROFILE_FILE, "r") as f:
        profile_data = json.load(f)
        
    basal_array = profile_data.get("basalprofile", [{"i": 0, "start": "00:00:00", "minutes": 0, "rate": 0.8}])
    
    with open(BASAL_FILE, "w") as f:
        json.dump(basal_array, f)

    # 2. Calcul IOB (Rendu SILENCIEUX avec capture_output=True)
    subprocess.run(
        ['oref0-calculate-iob', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE], 
        capture_output=True, 
        check=True
    )

    # 3. Calcul Meal (Rendu SILENCIEUX avec capture_output=True)
    subprocess.run([
        'oref0-meal', 
        PUMP_HISTORY_FILE, 
        PROFILE_FILE, 
        CLOCK_FILE, 
        GLUCOSE_FILE, 
        BASAL_FILE
    ], capture_output=True, check=True)

    # 4. Décision OpenAPS (Rendu SILENCIEUX, on ne garde que le résultat textuel)
    result = subprocess.run(
        ['oref0-determine-basal', IOB_FILE, CURRENTTEMP_FILE, GLUCOSE_FILE, PROFILE_FILE], 
        capture_output=True, 
        text=True,
        check=True
    )

    # On convertit le résultat en dictionnaire JSON
    recommendation = json.loads(result.stdout)
    
    # 5. Préparation de la réponse pour MATLAB
    if "rate" in recommendation:
        taux_insuline = recommendation["rate"]
    else:
        taux_insuline = profile_data.get("current_basal", 0.8)

    reponse_matlab = {
        "reason": recommendation.get("reason", "Aucune raison fournie"),
        "rate": taux_insuline,
        "duration": recommendation.get("duration", 30)
    }
    
    return reponse_matlab