from flask import Flask, request, jsonify
import dataTreatment as dt

app = Flask(__name__)

# ATTENTION : Route '/' pour correspondre à Matlab
@app.route('/', methods=['POST'])
def home():
    print("\n--- MESSAGE REÇU DE MATLAB ---")
    data = request.json
    print(f"Données brutes reçues : {data}")

    # Recherche intelligente des données patient
    target_data = data
    if isinstance(data, dict) and 'patient' in data:
        target_data = data['patient']
    elif isinstance(data, dict) and 'data' in data:
        target_data = data['data']
    
    # Appel du module de calcul
    dose_calculee = dt.process(target_data)

    print(f"--- RÉPONSE ENVOYÉE : {dose_calculee} U/h ---")

    # Format de réponse spécifique pour votre Matlab
    return jsonify({
        "status": "success",
        "nouvelle_valeur": dose_calculee,  # <-- Matlab attend ce mot précis !
        "unit": "U/h"
    })

if __name__ == '__main__':
    # '0.0.0.0' OBLIGATOIRE pour la connexion Wifi
    app.run(host='0.0.0.0', port=5000)