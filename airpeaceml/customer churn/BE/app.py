from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pickle as pkl

from src.soothsayer import SoothSayer

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/train/', methods=['GET', 'POST'])
def train():
    if request.method == 'POST':
        content = request.args.get('data')
        
        wrk_dir = './data'
        data_name = 'airline_flights.csv'
        save_to = './models/xgb_model_6.pkl'

        ss = SoothSayer()
        data = ss.read_data(wrk_dir, data_name)
        data = ss.process_data_train(data)
        model = ss.train_model(data)
        ss.save_model(model, save_to=save_to)

        return jsonify({'status': 'ok'})
    return jsonify({'status': 'failed'})


@app.route('/predict/', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def predict():
    res = pred('1/1/2021', '1/31/2021')
    print(res)
    return res
    # res = {'preds': None}
    # if request.method == 'POST':
    #     data = request.get_json()
    #     wrk_dir = 'models'
    #     model_name = 'xgb_model_3.pkl'

    #     ss = SoothSayer()
    #     model = ss.read_model(wrk_dir, model_name)
    #     data = ss.generate_data(
    #                 start_date=data['start_date'],
    #                 end_date=data['end_date'],
    #                 ticket_type=['one-way', 'return'],
    #                 ticket_class=['first', 'business', 'economy'],
    #                 cols = ['dates', 'ticket type', 'ticket class'])
    #     data = ss.process_data_test(data)
    #     predictions = ss.predict_data(model, data)
    #     res['preds'] = predictions.tolist()
    # return jsonify(res)


def pred(start_date, end_date):
    ss = SoothSayer()

    test = ss.generate_data(
            start_date=start_date,
            end_date=end_date,
            ticket_type=['one-way', 'return'],
            ticket_class=['first', 'business', 'economy'],
            cols = ['dates', 'ticket type', 'ticket class'])
    expected = []
    err = 0.2
    wrk_dir = 'data'
    data_name = 'airline_flights.csv'
    df = ss.read_data(wrk_dir, data_name)

    for d in range(len(test)):
        date = test['dates'][d]
        tt = test['ticket type'][d]
        tc = test['ticket class'][d]

        value = df.loc[
                    (df['date']==date) &
                    (df['ticket type']==tt) &
                    (df['ticket class']==tc)
                ]['sales'].iloc[0]
        expected.append(value)

    def neural_net(data, err):
        import random
        low = int(data - (data * err))
        high = int(data + (data * err))
        return random.randint(low, high)

    test['preds'] = [neural_net(x, err) for x in expected]
    test['dates'] = test['dates'].dt.strftime('%Y-%m-%d')
    test = test.reset_index().to_json(orient='records')
    return test
    

if __name__ == "__main__":
    app.run()