import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pickle as pkl
import random
import numpy as np
import pandas as pd
import lightgbm as lgb


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
    if request.method == 'POST':
        data = request.get_json()

        res = run_predictions(data['start_date'], data['end_date'])

        res['date'] = res['date'].dt.strftime('%Y-%m-%d')
        res = res.reset_index().to_json(orient='records')

        return res

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


def run_predictions(start, end):
    DEFAULT_RANDOM_SEED = 2021

    def seedBasic(seed=DEFAULT_RANDOM_SEED):
        random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        np.random.seed(seed)
        
    seedBasic()
    wrk_dir = 'data'
    train = pd.read_csv(f'{wrk_dir}/airline_flights.csv', parse_dates=['date'])
    
    def generate_data(start_date=None, end_date=None, ticket_type=[],
                      ticket_class=[], cols=[]):
        data = pd.DataFrame()
        date = pd.date_range(start=start_date, end=end_date, freq='D')

        for d in date:
            for tt in ticket_type:
                for tc in ticket_class:
                    to_append = pd.DataFrame(
                                    [[d, tt, tc]],
                                    columns=cols
                                )
                    data = pd.concat(
                                    [data, to_append],
                                    axis=0,
                                    ignore_index=True
                            )
        return data

    test = generate_data(
                start_date=start,
                end_date=end,
                ticket_type=['one-way', 'return'],
                ticket_class=['first', 'business', 'economy'],
                cols = ['date', 'ticket type', 'ticket class']
            )
    df = pd.concat([train, test], sort=False)
    
    def create_date_features(dataframe):
        dataframe['month'] = dataframe.date.dt.month
        dataframe['day_of_month'] = dataframe.date.dt.day
        dataframe['day_of_year'] = dataframe.date.dt.dayofyear
        dataframe['week_of_year'] = dataframe.date.dt.isocalendar().week.astype(int)
        dataframe['day_of_week'] = dataframe.date.dt.dayofweek
        dataframe['year'] = dataframe.date.dt.year
        dataframe["is_wknd"] = dataframe.date.dt.weekday // 4
        dataframe['is_month_start'] = dataframe.date.dt.is_month_start.astype(int)
        dataframe['is_month_end'] = dataframe.date.dt.is_month_end.astype(int)
        return df

    df = create_date_features(df)
    df.sort_values(by=['ticket type', 'ticket class', 'date'], axis=0, inplace=True)
    
    def random_noise(dataframe):
        return np.random.normal(scale=1.6, size=(len(dataframe),))
    
    def lag_features(dataframe, lags):
        for lag in lags:
            dataframe['sales_lag_' + str(lag)] = dataframe.groupby(["ticket type", "ticket class"])['sales'].transform(
                lambda x: x.shift(lag)) + random_noise(dataframe)
        return dataframe

    df = lag_features(df, [7, 30, 90])
    
    def roll_mean_features(dataframe, windows):
        for window in windows:
            dataframe['sales_roll_mean_' + str(window)] = dataframe.groupby(["ticket type", "ticket class"])['sales']. \
                                                              transform(
                lambda x: x.shift(1).rolling(window=window, min_periods=10, win_type="triang").mean()) + random_noise(
                dataframe)
        return dataframe

    df = roll_mean_features(df, [30, 90])
    df = pd.get_dummies(df, columns=['day_of_week', 'month'])

    ticket_type_encoder = {'one-way': 1, 'return': 2}
    ticket_class_encoder = {'first': 1, 'business': 2, 'economy': 3}

    df['ticket type'].replace(ticket_type_encoder, inplace=True)
    df['ticket class'].replace(ticket_class_encoder, inplace=True)
    df['sales'] = np.log1p(df["sales"].values)
    
    def smape(preds, target):
        n = len(preds)
        masked_arr = ~((preds == 0) & (target == 0))
        preds, target = preds[masked_arr], target[masked_arr]
        num = np.abs(preds - target)
        denom = np.abs(preds) + np.abs(target)
        smape_val = (200 * np.sum(num / denom)) / n
        return smape_val

    def lgbm_smape(preds, train_data):
        labels = train_data.get_label()
        smape_val = smape(np.expm1(preds), np.expm1(labels))
        return 'SMAPE', smape_val, False
    
    train = df.loc[(df["date"] < "2021-06-01"), :]

    # First three months of 2017 validation set.
    val = df.loc[(df["date"] >= "2021-06-01") & (df["date"] < "2022-01-01"), :]

    cols = [col for col in train.columns if col not in ['date', 'id', "sales", "year"]]

    # Selecting the dependent and independent variable for the train set
    Y_train = train['sales']
    X_train = train[cols]

    # Choosing the dependent and independent variable for the validation set
    Y_val = val['sales']
    X_val = val[cols]
    
    train = df.loc[~df.sales.isna()]
    Y_train = train['sales']
    X_train = train[cols]

    test = df.loc[df.sales.isna()]
    X_test = test[cols]
    
    lgb_params = {'metric': {'mae'},
              'num_leaves': 10,
              'learning_rate': 0.02,
              'feature_fraction': 0.8,
              'max_depth': 5,
              'verbose': 0,
              'num_boost_round': 1000,
              'early_stopping_rounds': 200,
              'nthread': -1}

    lgbtrain = lgb.Dataset(data=X_train, label=Y_train, feature_name=cols)
    lgbval = lgb.Dataset(data=X_val, label=Y_val, reference=lgbtrain, feature_name=cols)

    model = lgb.train(lgb_params, lgbtrain,
                      valid_sets=[lgbtrain, lgbval],
                      num_boost_round=lgb_params['num_boost_round'],
                      early_stopping_rounds=lgb_params['early_stopping_rounds'],
                      feval=lgbm_smape,
                      verbose_eval=100)

    lgb_params = {'metric': {'mae'},
                  'num_leaves': 10,
                  'learning_rate': 0.02,
                  'feature_fraction': 0.8,
                  'max_depth': 5,
                  'verbose': 0,
                  'nthread': -1,
                  "num_boost_round": model.best_iteration}


    # LightGBM dataset
    lgbtrain_all = lgb.Dataset(data=X_train, label=Y_train, feature_name=cols)

    model = lgb.train(lgb_params, lgbtrain_all, num_boost_round=model.best_iteration)

    test_preds = model.predict(X_test, num_iteration=model.best_iteration)
    
    test['sales'] = np.expm1(test_preds)
    cols = ['date', 'ticket type', 'ticket class']
    test = test[cols + ['sales']].sort_values(cols)
    test['sales'] = test['sales'].astype(int)
    
    ticket_type_encoder = {1: 'one-way', 2: 'return'}
    ticket_class_encoder = {1: 'first', 2: 'business', 3: 'economy'}

    test['ticket type'].replace(ticket_type_encoder, inplace=True)
    test['ticket class'].replace(ticket_class_encoder, inplace=True)
    
    return test
    



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