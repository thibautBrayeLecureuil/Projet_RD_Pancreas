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
    # 1. On lit l'horloge
    with open(CLOCK_FILE, "r") as f:
        date_str = json.loads(f.read())
        
    # 2. On avance le temps de 10 secondes
    current_dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00")) + datetime.timedelta(seconds=10)
    
    # 3. On prépare les DEUX formats de date exigés par OpenAPS
    date_string = current_dt.isoformat().replace("+00:00", "") + "Z"
    date_ms = int(current_dt.timestamp() * 1000)

    # L'objet glucose est maintenant parfait pour OpenAPS
    glucose_data = {
        "date": date_ms,            # Millisecondes pour les calculs internes
        "dateString": date_string,  # Texte pour la lecture
        "sgv": data,
        "direction": "Flat",
        "noise": 1
    }

    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())
        
    glucose_file.append(glucose_data)
   
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)

    # 5. On sauvegarde la nouvelle horloge pour la prochaine boucle


    return callLoop()

def callLoop():
    # 1. Calcul IOB : On capture le texte ET on l'écrit dans le fichier iob.json !
    iob_result = subprocess.run(
        ['oref0-calculate-iob', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE], 
        capture_output=True, 
        text=True, # Important pour récupérer du texte et pas des bytes
        check=True
    )
    # On sauvegarde le résultat dans le fichier pour l'étape suivante
    with open(IOB_FILE, "w") as f:
        f.write(iob_result.stdout)

    # 2. Calcul Meal (Silencieux)
    subprocess.run([
        'oref0-meal', 
        PUMP_HISTORY_FILE, 
        PROFILE_FILE, 
        CLOCK_FILE, 
        GLUCOSE_FILE, 
        BASAL_FILE
    ], capture_output=True, check=True)

    # 3. Décision finale
    result = subprocess.run(
        ['oref0-determine-basal', IOB_FILE, CURRENTTEMP_FILE, GLUCOSE_FILE, PROFILE_FILE], 
        capture_output=True, 
        text=True
    )
    
    # SÉCURITÉ : Si oref0 plante et ne renvoie rien, on affiche l'erreur et on maintient le basal
    if not result.stdout.strip():
        print("ERREUR OPENAPS (oref0-determine-basal a crashé) :")
        print(result.stderr) # Ça affichera le vrai problème dans ton terminal
        return 0.8
        
    recommendation = json.loads(result.stdout)
    
    print(" RAISON OPENAPS :", recommendation.get("reason", "Aucune explication"))
    
    if "rate" in recommendation:
        taux_insuline = recommendation["rate"]
    else:
        taux_insuline = 0
        
    try:
        # On lit l'heure virtuelle
        with open(CLOCK_FILE, "r") as f:
            current_time_str = json.loads(f.read())
            
        # On lit l'ancien historique
        with open(PUMP_HISTORY_FILE, "r") as f:
            pump_history = json.loads(f.read())
    except Exception:
        # Si le fichier n'existe pas ou est mal formaté, on part de zéro
        pump_history = []
        
    event_rate = {
        "_type": "TempBasal",
        "temp": "absolute",
        "rate": taux_insuline,
        "timestamp": current_time_str
    }
    
    event_duration = {
        "_type": "TempBasalDuration",
        "duration (min)": 30, # OpenAPS met toujours des basals de 30 minutes par défaut
        "timestamp": current_time_str
    }
    
    # On les insère au début (en index 0).
    pump_history.insert(0, event_rate)
    pump_history.insert(0, event_duration)
    
    # On garde juste les 50 derniers pour ne pas faire bugger la Raspberry
    pump_history = pump_history[:50]
    
    # On écrase le fichier avec le nouvel historique
    with open(PUMP_HISTORY_FILE, "w") as f:
        json.dump(pump_history, f, indent=4)
    
    return taux_insuline