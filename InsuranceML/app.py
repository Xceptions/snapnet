from audioop import cross
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import joblib

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/pred/", methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def pred():
    print("pred called")
    result = {'error': 'method not post'}
    if request.method == 'POST':
        print("got here")
        data = request.get_json()
        print(data)

        use_cols = ['MINKGEM', 'PPERSAUT', 'MRELGE', 'MINK7512',
                    'MOPLHOOG', 'PBRAND', 'MKOOPKLA', 'MGEMOMV']
        use_vals = [vals for key,vals in data.items()]
        df = pd.DataFrame(columns=use_cols)
        df.loc[0] = use_vals

        print(df)
        
        rf = joblib.load("./models/rf_model.joblib")
        print("loaded")
        pred = rf.predict(df)
        print(f'predictions are in {pred}')
        result = {'prediction': str(pred[0])}

    return jsonify(result)

if __name__ == "__main__":
    app.run()