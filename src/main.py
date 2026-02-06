from flask import Flask, request, jsonify
import dataTreatment as dt

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control_loop():

    data = request.json

    print("Received data:", data)
    dataresponse = dt.process(data['patients'][0])

    return jsonify(dataresponse)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)