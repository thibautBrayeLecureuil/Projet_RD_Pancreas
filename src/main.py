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

    dt.process(data['patients'][0])

    return jsonify({"insuline": "aucune idée le sang et c derbanch et " })

@app.route('/historique', methods=['POST'])
def historique_loop():

    data = request.json

    if "size" in data :
        createHistotique(data["size"])
    else :
        createHistotique()

def createHistotique(size=5):

    date = datetime.datetime.now(datetime.timezone.utc)
    minute = date.minute
    hour = date.hour
    day = date.day
    datas = []

    for i in range(size):

        date.hour += 1

        diff = minute - 5
        if diff < 0 :
            minute = 60 + diff
            hour -= 1
            if hour < 0 :
                hour = 23
                day = day - 1
        else :
            minute = diff

        date = datetime.datetime(date.year, date.month, day, hour, minute, date.second)
        dateString = date.isoformat() + "Z"

        glucose_data = {
            "date": dateString,
            "sgv": 122,
            "direction": "Flat",
            "noise": 1
        }

        datas.append(glucose_data)
    datas.reverse()

    with open(GLUCOSE_FILE, "w") as f:
        json.dump(datas, f)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)