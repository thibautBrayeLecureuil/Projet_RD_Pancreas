from flask import Flask, render_template, request, jsonify
import dataTreatment as dt
import datetime
import json
import os
import random

PORT=8081

PATH = os.path.dirname(os.path.abspath(__file__))[:-4]
PATH_RESSOURCES = PATH + "/ressources"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"
PUMP_HISTORY_FILE = PATH_RESSOURCES + "/pumphistory.json"
PROFILE_FILE = PATH_RESSOURCES + "/profile.json"

app = Flask(__name__, template_folder=PATH + "/web/templates", static_folder=PATH + "/web/static")

'''
Route pour recevoir les données de glycémie et calculer la dose d'insuline à injecter
'''
@app.route('/control', methods=['POST'])
def control_loop():
    data = request.json
    response = dt.process(data['glycemie'])
    return jsonify({"insuline": response })

 '''
 Historique bidon basé sur une valeur de Matlab
 '''
@app.route('/historique', methods=['POST'])
def historique_loop():
    data = request.json
    createHistorique(data.get("size", 8640), data.get("basal", 120))
    return jsonify({"response": "Done" })

'''
Route pour afficher la page web avec les données de profil
'''
@app.route('/')
def web():
    with open(PROFILE_FILE) as f:
        data = json.load(f)
        f.close()

    return render_template("index.html", profile=data)

'''
Route pour mettre à jour le profil de la pompe
'''
@app.route('/updateprofile', methods=['POST'])
def update_profile():
    data = request.json

    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f)
        f.close()

'''
Route pour recevoir un historique de glycémie depuis Matlab et le stocker
'''
@app.route('/historiqueMatlab', methods=['POST'])
def historique_matlab():
    data = request.json
    createHistoriqueMatlab(data["values"])
    return jsonify({"response": "Done" })
 
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

        date = date - datetime.timedelta(seconds=10)
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
        date = date - datetime.timedelta(seconds=10)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)