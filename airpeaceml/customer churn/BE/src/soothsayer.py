### SOOTHSAYER
import numpy as np
import pandas as pd
import pickle as pkl
import xgboost as xgb

class SoothSayer:

    def read_model(self, wrk_dir, model_name):
        return pkl.load(open(f'{wrk_dir}/{model_name}', 'rb'))
    
    def read_data(self, wrk_dir, data_name):
        return pd.read_csv(f'{wrk_dir}/{data_name}', parse_dates=['date'])

    def generate_data(self, start_date=None,
                      end_date=None, ticket_type=[],
                      ticket_class=[], cols=[]):
        data = pd.DataFrame()
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        for d in dates:
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
    
    def process_data_train(self, data):
        ticket_type_encoder = {'one-way': 1, 'return': 2}
        ticket_class_encoder = {'first': 1, 'business': 2, 'economy': 3}

        data['ticket type'].replace(ticket_type_encoder, inplace=True)
        data['ticket class'].replace(ticket_class_encoder, inplace=True)
        return data[['ticket type', 'ticket class']]

    def process_data_test(self, data):
        ticket_type_encoder = {'one-way': 1, 'return': 2}
        ticket_class_encoder = {'first': 1, 'business': 2, 'economy': 3}

        data['ticket type'].replace(ticket_type_encoder, inplace=True)
        data['ticket class'].replace(ticket_class_encoder, inplace=True)
        return data[['ticket type', 'ticket class']]
    
    def train_model(self, data=None):
        model = xgb.XGBRegressor(max_depth=7, num_leaves=200)
        model.fit(tt_x, tt_y)

    def predict_data(self, model, data):
        return model.predict(data)
    
    def save_model(self, model, save_to='./model.pkl'):
        pkl.dump(model, open(save_to, "wb"))
