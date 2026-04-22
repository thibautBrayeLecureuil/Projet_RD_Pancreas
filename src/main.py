from flask import Flask, request, jsonify
import dataTreatment as dt
import datetime
import json
import os
import random

PATH = os.path.dirname(os.path.abspath(__file__))[:-4]

PATH_RESSOURCES = PATH + "/ressources"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"

last_recomended_rate = 0

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():
    data = request.json
    
    # On laisse dataTreatment faire tout le travail (y compris avancer l'horloge de 5 min)
    response = dt.process(data['glycemie'])

    return jsonify({"insuline": response })

@app.route('/historique', methods=['POST'])
def historique_loop():

    data = request.json
    createHistorique(data["size"] if "size" in data else 8640, data["basal"] if "basal" in data else 120)

    return jsonify({"response": "Done" })

def createHistorique(size=8640, basal=120):

    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []

    for i in range(size):
            
        date = date - datetime.timedelta(seconds=10)
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
        
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

        
@app.route('/historiqueMatlab', methods=['POST'])
def historique_matlab():

    data = request.json
    createHistoriqueMatlab(data["values"])
    return jsonify({"response": "Done" })

def createHistoriqueMatlab(values):

    date = datetime.datetime.now(datetime.timezone.utc)
    datas = []

    values.reverse()

    for value in values:
            
        date = date - datetime.timedelta(seconds=10)
        date_string = date.isoformat().replace("+00:00", "") + "Z"

        glucose_data = {
            "date": int(date.timestamp() * 1000),
            "dateString": date_string,
            "sgv": value,
            "direction": "Flat",
            "noise": 1,
        }

        datas.append(glucose_data)
        
    with open(CLOCK_FILE, "w") as f:
        json.dump(date_string, f)

    datas.reverse()

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)