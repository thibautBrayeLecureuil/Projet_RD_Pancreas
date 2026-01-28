from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():

    data = request.json
    glucose = data.get('glucose')

    if glucose > 150:
        print("Trop de Glucose")
    else:
        print("Pas trop de Glucose")
    # ---------------------------------------------------------------

    return jsonify({
        "status": "success",
        "insulin_dose": 100,
        "unit": "pmol/min"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)