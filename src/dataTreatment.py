from flask import jsonify
import subprocess
import datetime
import random
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

with open(os.path.join(PATH, "config.json")) as f:
    config = json.load(f)
    f.close()

TIMEDELTAMIN = config.get("time_delta_minute", 5)

'''
Fonction pour traiter les données de glycémie, mettre à jour les fichiers nécessaires et appeler Oref0 pour obtenir une recommandation d'insuline
'''
def process(data):

    with open(CLOCK_FILE, "r") as f:
        date_str = json.loads(f.read())
        
    current_dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00")) + datetime.timedelta(minutes=TIMEDELTAMIN)
    
    date_string = current_dt.isoformat().replace("+00:00", "Z")
    date_ms = int(current_dt.timestamp() * 1000)

    glucose_data = {
        "date": date_ms,
        "dateString": date_string,
        "sgv": data,
        "direction": "Flat",
        "noise": 1
    }

    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())
        
    glucose_file.insert(0, glucose_data)
   
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)

    return callLoop()


'''
appel d'oref0 pour obtenir une recommandation d'insuline basée sur les données actuelles de glycémie, le profil de la pompe, l'historique de la pompe et les repas
'''
def callLoop():

    iob_result = subprocess.run(
        ['oref0-calculate-iob', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE], 
        capture_output=True, text=True, check=True
    )
    with open(IOB_FILE, "w") as f:
        f.write(iob_result.stdout)

    subprocess.run([
        'oref0-meal', 
        PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE, GLUCOSE_FILE, BASAL_FILE
    ], capture_output=True, check=True)
    
    with open(CLOCK_FILE, "r") as f:
        current_time_str = json.loads(f.read())

    updatePumpHistory(current_time_str)

    result = subprocess.run(
        ['oref0-determine-basal', IOB_FILE, CURRENTTEMP_FILE, GLUCOSE_FILE, 
         PROFILE_FILE, '--meal', MEAL_FILE, '--currentTime', current_time_str],
        capture_output=True, text=True
    )
    
    if not result.stdout.strip():
        print("ERREUR OPENAPS :", result.stderr)
        return 0.8
        
    recommendation = json.loads(result.stdout)
    
    print(" RAISON OPENAPS :", recommendation.get("reason", "Aucune explication"))
    
    if "rate" in recommendation:
        taux_insuline = recommendation["rate"]
    else:
        taux_insuline = 0.8
        
    return taux_insuline


'''
Mise à jour de l'historique de la pompe avec un nouvel événement de repas ou de basal
'''
def updatePumpHistory(date):
    with open(PUMP_HISTORY_FILE, 'r') as f:
        pump_history = json.loads(f.read())

    with open(MEAL_FILE, 'r') as f:
        meal_data = json.loads(f.read())

    if meal_data:
        event_rate =  {
            "timestamp": date,
            "carbs": meal_data.get("carbs"),
        }

    else:
        event_rate =  {
            "timestamp": date,
            "carbs": 0,
        }

    pump_history.insert(0, event_rate)
    
    with open(PUMP_HISTORY_FILE, 'w') as f:
        json.dump(pump_history, f)

'''
Historique bidon basé sur une valeur de Matlab
'''
def createHistorique(size=8640, basal=120):
    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []
    
    date_string = date.isoformat().replace("+00:00", "Z")
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    for i in range(size):

        date = date - datetime.timedelta(minutes=TIMEDELTAMIN)
        date_string = date.isoformat().replace("+00:00", "Z")
        variation = random.randint(-20, 20)
        glucose_data = {
            "date": int(date.timestamp() * 1000),
            "dateString": date_string,
            "sgv": basal + variation,
            "direction": "Flat",
            "noise": 1,
        }
        datas.insert(0, glucose_data)

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

'''
Historique basé sur des valeurs envoyées par Matlab
'''
def createHistoriqueMatlab(values):
    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []
    pump_history(date)
    values.reverse()
    
    date_string = date.isoformat().replace("+00:00", "Z")
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    for value in values:
        date = date - datetime.timedelta(minutes=TIMEDELTAMIN)
        date_string = date.isoformat().replace("+00:00", "Z")
        glucose_data = {
            "date": int(date.timestamp() * 1000),
            "dateString": date_string,
            "sgv": float(value),
            "direction": "Flat",
            "noise": 1,
        }
        datas.append(glucose_data)
    
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

    return jsonify({"response": "Profile updated" })

'''
Faux historique de la pompe pour tester la partie calcul de l'insuline
Probablement à modifier pour être plus réaliste
'''
def pump_history(date):
    pump_history_data = []
    event_rate =  {
        "timestamp": date.isoformat().replace("+00:00", "Z"),
        "carbs": 40
    }
    pump_history_data.append(event_rate)

    with open(PUMP_HISTORY_FILE, "w") as f:
        json.dump(pump_history_data, f, indent=4)