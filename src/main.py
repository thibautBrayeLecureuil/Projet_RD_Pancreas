from flask import Flask, request, jsonify
import dataTreatment as dt
import datetime
import json

PATH_RESSOURCES = "../ressources"
GLUCOSE_FILE = PATH_RESSOURCES + "/glucose.json"

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():

    data = request.json

    response = dt.process(data['patients'][0])

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
        dateString = date.isoformat() + "Z"

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