# python/train_models.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import joblib

df = pd.read_csv('features_all.csv')
X, y = df.drop('label', axis=1), df['label']

clf = RandomForestClassifier(n_estimators=200, max_depth=10)
clf.fit(X, y)

iso = IsolationForest(contamination=0.01)
iso.fit(X)

joblib.dump(clf, 'rf_model.pkl')
joblib.dump(iso, 'iso_model.pkl')
print("Models trained and saved: rf_model.pkl, iso_model.pkl")
