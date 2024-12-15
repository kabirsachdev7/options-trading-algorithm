from flask import Blueprint, request, jsonify
import pandas as pd
from strategies.strategy_optimization import optimize_strategy
import tensorflow as tf
import numpy as np
from models.lstm_model import build_lstm_model

api = Blueprint('api', __name__)

@api.route('/recommendations', methods=['GET'])
def get_recommendations():
    ticker = request.args.get('ticker', 'AAPL')
    data = pd.read_csv(f'data/merged_data_with_features_{ticker}.csv')
    recommendations = optimize_strategy(data)
    return jsonify(recommendations)

@api.route('/predict', methods=['POST'])
def predict_option_price():
    content = request.json
    features = content['features']
    features = np.array(features).reshape(1, -1)
    model = tf.keras.models.load_model('models/lstm_option_pricing.h5')
    prediction = model.predict(features)
    return jsonify({'predicted_price': prediction[0][0]})
