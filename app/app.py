# dependencies
import tensorflow as tf 
import pandas as pd
import numpy as np
import os
from flask import Flask, request, Response, jsonify, send_from_directory, abort 
import sys
import json
# get relative path
path = os.getcwd()

# load in saved model
model = tf.keras.models.load_model(os.path.join(path, 'saved_model', 'lstm'))

# initalize flask app
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def make_prediction():
    try:
        request_data = request.get_json()
        time = request_data['time']

    except:
        time = request.args.get('time')

    time = pd.to_datetime(time)
    try:
        # import processed test data
        data = pd.read_csv(os.path.join(path,'processed_data.csv'))
        data['date_time'] = pd.to_datetime(data['date_time'])
        test_data = data.loc[data['date_time'] == str(time)].index
        test = data.iloc[test_data[0]-23 : test_data[0] + 1]
        data = data.set_index('date_time')
        test = test.set_index('date_time')
        prior_temps = test['internalTemperature'].tolist()
        test = np.array(test, dtype=np.float32)
        ds = tf.keras.preprocessing.timeseries_dataset_from_array(
            data=test,
            targets=None,
            sequence_length=24,
            sequence_stride=1,
            shuffle=False,
            batch_size=1,)

        prediction = model.predict(ds)
        future_hour = prediction[0][3].round(2)
        print("Prediction made is: ", future_hour, " degrees Celsius!")
        response = {
            'prediction': future_hour,
            'temperatures': prior_temps
        }
        print(response, file=sys.stderr)
        return Response(response=response, status=200, mimetype='application/json')
    except:
        message = 'Error with app.'
        response = {
            "Error": message
        }
        print('Error! Could not find requested timeframe.')
        return Response(response=response, status=400, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port=3000)