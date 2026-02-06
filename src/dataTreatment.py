import subprocess
import datetime
import json

IOB_FILE = "../ressources/iob.json"
GLUCOSE_FILE = "../ressources/glucose.json"
PROFILE_FILE = "../ressources/profile.json"
CLOCK_FILE = "../ressources/clock.json"
PUMP_HISTORY_FILE = "../ressources/pumphistory.json"
CURRENTTEMP_FILE = "../ressources/currenttemp.json"
MEAL_FILE = "../ressources/meal.json"

def process(data):

    date = datetime.datetime.now()
    dateString = date.isoformat() + "Z"
    
    glucose_data = {
        "date": date.timestamp(),
        "dateString": dateString,
        "sgv": data["Gb"],
        "direction": "Flat",
        "noise": 1
    }

    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())

    glucose_file.append(glucose_data)
    
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(glucose_file, f)


    #appel de oref0
    output = callLoop()

    return output

def callLoop():

        
    output = subprocess.run(['oref0-calculate-iob', PUMP_HISTORY_FILE,PROFILE_FILE ,CLOCK_FILE])
    output = subprocess.run(['oref0-meal', PUMP_HISTORY_FILE, PROFILE_FILE, CLOCK_FILE, GLUCOSE_FILE])
    output = subprocess.run(['oref0-determine-basal', IOB_FILE, CURRENTTEMP_FILE, GLUCOSE_FILE, PROFILE_FILE, MEAL_FILE])
    
    return output