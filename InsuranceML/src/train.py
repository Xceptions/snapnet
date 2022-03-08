import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import joblib


data = pd.read_csv('../data/caravan-insurance-challenge.csv')

use_cols = ['MINKGEM', 'PPERSAUT', 'MRELGE', 'MINK7512', 'MOPLHOOG', 'PBRAND', 'MKOOPKLA', 'MGEMOMV']
df = data[use_cols]
y = data['CARAVAN']

clf = RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
                       max_depth=15, max_features='auto', max_leaf_nodes=None,
                       min_impurity_decrease=0.0,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, n_estimators=500, n_jobs=1,
                       oob_score=False, random_state=42, verbose=1,
                       warm_start=False)

clf.fit(df, y)
joblib.dump(clf, "../models/rf_model.joblib")