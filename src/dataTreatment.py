import subprocess
import datetime
import json
import os

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_RESSOURCES = PATH + "/ressources"
IOB_FILE = PATH_RESSOURCES + "/iob.json"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
PROFILE_FILE = PATH_RESSOURCES + "/profile.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"
PUMP_HISTORY_FILE = PATH_RESSOURCES + "/pumphistory.json"
CURRENTTEMP_FILE = PATH_RESSOURCES + "/currenttemp.json"
MEAL_FILE = PATH_RESSOURCES + "/meal.json"
BASAL_FILE = PATH_RESSOURCES + "/basalprofile.json"


def _parse_clock(raw_clock):
    if isinstance(raw_clock, str):
        return datetime.datetime.fromisoformat(raw_clock.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    return datetime.datetime.now(datetime.timezone.utc)

def process(data):

    with open(CLOCK_FILE, "r") as f:
        date = json.loads(f.read())
        
    current_dt = _parse_clock(date) + datetime.timedelta(seconds=5)
    date_string = current_dt.isoformat().replace("+00:00", "") + "Z"

    glucose_data = {
        "date": int(current_dt.timestamp() * 1000),
        "dateString": date_string,
        "sgv": data,
        "direction": "Flat",
        "noise": 1,
    }

    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())
        f.close()
        
    # oref0 expects most recent glucose entries first.
    glucose_file.insert(0, glucose_data)
   
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)
        f.close()

    return callLoop()

def callLoop():
    
    subprocess.run(['oref0-calculate-iob', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE], check=True, capture_output=True)

    subprocess.run([
        'oref0-meal', 
        PUMP_HISTORY_FILE, 
        PROFILE_FILE, 
        CLOCK_FILE, 
        GLUCOSE_FILE, 
        BASAL_FILE
    ], check=True)

    result = subprocess.run(
        ['oref0-determine-basal', IOB_FILE, CURRENTTEMP_FILE, GLUCOSE_FILE, PROFILE_FILE], 
        capture_output=True, 
        text=True,
        check=True
    )
    
    recommendation = json.loads(result.stdout)
    print(recommendation)
    
    if "rate" in recommendation:
        taux_insuline = recommendation["rate"]
    else:
        taux_insuline = 0.8
    
    return taux_insuline