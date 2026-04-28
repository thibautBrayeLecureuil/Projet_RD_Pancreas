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
    try:
        with open(CLOCK_FILE, "r") as f:
            date_str = json.loads(f.read())
    except:
        date_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
        
    current_dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00")) + datetime.timedelta(minutes=5)
    
    date_string = current_dt.isoformat().replace("+00:00", "") + "Z"
    date_ms = int(current_dt.timestamp() * 1000)

    glucose_data = {
        "date": date_ms,
        "dateString": date_string,
        "sgv": float(data),
        "direction": "Flat",
        "noise": 1
    }

    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    try:
        with open(GLUCOSE_FILE, 'r') as f:
            glucose_file = json.loads(f.read())
    except:
        glucose_file = []
        
    glucose_file.insert(0, glucose_data)
    glucose_file = glucose_file[:288] 
   
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)

    return callLoop()

def callLoop():
    iob_result = subprocess.run(
        ['oref0-calculate-iob', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE], 
        capture_output=True, text=True, check=True
    )
    with open(IOB_FILE, "w") as f:
        f.write(iob_result.stdout)

    subprocess.run([
        'oref0-meal', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE, GLUCOSE_FILE, BASAL_FILE
    ], capture_output=True, check=True)

    with open(CLOCK_FILE, "r") as f:
        current_time_str = json.loads(f.read())

    result = subprocess.run(
        [
            'oref0-determine-basal', 
            IOB_FILE, 
            CURRENTTEMP_FILE, 
            GLUCOSE_FILE, 
            PROFILE_FILE,
            '--meal', MEAL_FILE,
            '--currentTime', current_time_str
        ], 
        capture_output=True, text=True
    )
    
    if not result.stdout.strip():
        print("ERREUR OPENAPS :", result.stderr)
        return 0.8
        
    recommendation = json.loads(result.stdout)
    print(" RAISON OPENAPS :", recommendation.get("reason", "Aucune explication"))
    
    taux_insuline = recommendation.get("rate", 0.8)

    try:
        with open(PUMP_HISTORY_FILE, 'r') as f:
            pump_history = json.loads(f.read())
    except:
        pump_history = []

    event_rate = {
        "_type": "TempBasal",
        "temp": "absolute",
        "rate": taux_insuline,
        "timestamp": current_time_str
    }
    event_duration = {
        "_type": "TempBasalDuration",
        "duration (min)": 30,
        "timestamp": current_time_str
    }
    
    
    pump_history.insert(0, event_rate)
    pump_history.insert(0, event_duration)
    pump_history = pump_history[:50]
    
    with open(PUMP_HISTORY_FILE, 'w') as f:
        json.dump(pump_history, f, indent=4)

    current_temp = {
        "duration": 30,
        "rate": taux_insuline,
        "temp": "absolute",
        "timestamp": current_time_str
    }
    with open(CURRENTTEMP_FILE, "w") as f:
        json.dump(current_temp, f, indent=4)

    return taux_insuline