from flask import Flask, request, jsonify
import dataTreatment as dt
import subprocess

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():

    data = request.json
    
    pwd = subprocess.run(['pwd'])

    print("Current directory:", pwd)

    print("Received data:", data)
    dataresponse = dt.process(data['patients'][0])

    return jsonify(dataresponse)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)