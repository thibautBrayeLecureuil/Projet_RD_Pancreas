from flask import Flask, request, jsonify
import dataTreatment as dt
import datetime
import json
import os

PATH = os.path.dirname(os.path.abspath(__file__))[:-4]

PATH_RESSOURCES = PATH + "/ressources"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"
CLOCK_FILE = PATH_RESSOURCES + "/clock.json"

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():

    data = request.json
    
    with open(GLUCOSE_FILE, 'r') as f:
        glucose_file = json.loads(f.read())

    if len(glucose_file) > 0:
        latest_glucose = max(
            glucose_file,
            key=lambda entry: datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
        )
        next_clock = (
            datetime.datetime.fromisoformat(latest_glucose["date"].replace("Z", "+00:00"))
            + datetime.timedelta(minutes=5)
        )
    else:
        next_clock = datetime.datetime.now(datetime.timezone.utc)
        
    with open(CLOCK_FILE, "w") as f:
        json.dump(next_clock.isoformat().replace("+00:00", "") + "Z", f)
        
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
            
        date = date - datetime.timedelta(minutes=5)
        dateString = date.isoformat().replace("+00:00", "") + "Z"

        glucose_data = {
            "date": dateString,
            "sgv": basal,
            "direction": "Flat",
            "noise": 1
        }

        datas.append(glucose_data)

    datas.reverse()

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)