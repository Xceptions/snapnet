import requests
import unittest


class AppTests(unittest.TestCase):
    def setUp(self):
        self.data = {'start_time': '1/2/2021', 'end_time': '2/2/2021'}

    # def test_api(self):
    #     url = 'http://localhost:5000/api/'
    #     res = requests.post(url, json=self.data)
    #     print(f'the result is {res.text}')
    #     self.assertEqual(type(res), str)

    def test_train(self):
        url = 'http://localhost:5000/train/'
        res = requests.post(url, json=self.data)
        print(res)
        self.assertEqual(res.content.status, "ok")

    # def test_predictions(self):
    #     wrk_dir = '../../models'
    #     model_name = 'xgb_model_3.pkl'

    #     ss = SoothSayer()
    #     model = ss.read_model(wrk_dir, model_name)
    #     data = ss.generate_data(
    #                 start_date='1/1/2022',
    #                 end_date='1/31/2022',
    #                 ticket_type=['one-way', 'return'],
    #                 ticket_class=['first', 'business', 'economy'],
    #                 cols = ['dates', 'ticket type', 'ticket class'])
    #     data = ss.process_data_test(data)
    #     predictions = ss.predict_data(model, data)
    #     self.assertEqual(type(predictions), list)


if __name__ == "__main__":
    unittest.main()