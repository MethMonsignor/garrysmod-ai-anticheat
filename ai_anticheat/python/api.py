# python/api.py

from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
clf = joblib.load('rf_model.pkl')
iso = joblib.load('iso_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    feat = np.array([[data[k] for k in sorted(data)]])
    class_prob = clf.predict_proba(feat).tolist()[0]
    anomaly_score = float(iso.decision_function(feat))
    return jsonify({
        "vector_probabilities": dict(zip(clf.classes_, class_prob)),
        "anomaly_score": anomaly_score
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
