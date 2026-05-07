from flask import Flask, render_template, request, jsonify
import dataTreatment as dt
import json
import os

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
    dt.createHistorique(data.get("size", 8640), data.get("basal", 120))
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
    dt.createHistoriqueMatlab(data["values"])
    return jsonify({"response": "Done" })
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)