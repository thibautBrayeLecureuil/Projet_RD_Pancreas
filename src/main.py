from flask import Flask, render_template, request, jsonify
import dataTreatment as dt
import datetime
import json
import os
import random

PATH = os.path.dirname(os.path.abspath(__file__))[:-4]
PATH_RESSOURCES = PATH + "/ressources"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"
PUMP_HISTORY_FILE = PATH_RESSOURCES + "/pumphistory.json"
PROFILE_FILE = PATH_RESSOURCES + "/profile.json"

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():
    data = request.json
    response = dt.process(data['glycemie'])
    return jsonify({"insuline": response })

@app.route('/historique', methods=['POST'])
def historique_loop():
    data = request.json
    createHistorique(data.get("size", 8640), data.get("basal", 120))
    return jsonify({"response": "Done" })

def createHistorique(size=8640, basal=120):
    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []
    
    date_string = date.isoformat().replace("+00:00", "") + "Z"
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    for i in range(size):
        # CRUCIAL : minutes=5 pour simuler correctement l'historique
        date = date - datetime.timedelta(minutes=5)
        date_string = date.isoformat().replace("+00:00", "") + "Z"
        variation = random.randint(-20, 20)
        glucose_data = {
            "date": int(date.timestamp() * 1000),
            "dateString": date_string,
            "sgv": basal + variation,
            "direction": "Flat",
            "noise": 1,
        }
        datas.append(glucose_data)

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

@app.route('/historiqueMatlab', methods=['POST'])
def historique_matlab():
    data = request.json
    createHistoriqueMatlab(data["values"])
    return jsonify({"response": "Done" })

def pump_history(date):
    pump_history_data = []
    event_rate =  {
        "timestamp": date.isoformat().replace("+00:00", "") + "Z",
        "carbs": 40
    }
    pump_history_data.append(event_rate)
    with open(PUMP_HISTORY_FILE, "w") as f:
        json.dump(pump_history_data, f, indent=4)

def createHistoriqueMatlab(values):
    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []
    pump_history(date)
    values.reverse()
    
    date_string = date.isoformat().replace("+00:00", "") + "Z"
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    for value in values:
        # CRUCIAL : minutes=5
        date = date - datetime.timedelta(minutes=5)
        date_string = date.isoformat().replace("+00:00", "") + "Z"
        glucose_data = {
            "date": int(date.timestamp() * 1000),
            "dateString": date_string,
            "sgv": float(value),
            "direction": "Flat",
            "noise": 1,
        }
        datas.append(glucose_data)
    
    # Inutile de reverse ici puisque la plus récente est déjà au début grâce à notre boucle !
    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

@app.route('/')
def web():
    with open(PROFILE_FILE) as f:
        data = json.load(f)
    return render_template(PATH + "\\web\\index.html", profile=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)