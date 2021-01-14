from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api
import ktrain
from waitress import serve
import yaml

app = Flask(__name__)
CORS(app)


@app.route('/categorize', methods=['POST'])
def get():
    predictions = predictor.predict(request.json['text'], return_proba=True)
    categories = predictor.get_classes()
    result = {}
    for i in range(len(categories)):
        result[categories[i]] = predictions[i].item()
    return jsonify(result)


with open(r'../Config/model.yaml', encoding='utf-8') as file:
    config = yaml.full_load(file)

predictor = ktrain.load_predictor(config['model-save-path'])
predictor.predict('', return_proba=True)
api = Api(app)
if __name__ == '__main__':
    print(f'{datetime.now()} - ready')
    serve(app, host='0.0.0.0', port=8000)
