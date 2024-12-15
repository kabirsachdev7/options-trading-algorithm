import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

def create_transformer_data(data, features, target, time_steps=60):
    """
    Prepare data for Transformer model.
    """
    X = data[features].values
    y = data[target].values
    X_transformer, y_transformer = [], []
    for i in range(time_steps, len(X)):
        X_transformer.append(X[i - time_steps:i])
        y_transformer.append(y[i])
    X_transformer, y_transformer = np.array(X_transformer), np.array(y_transformer)
    return X_transformer, y_transformer

def build_transformer_model(input_shape, num_heads=4, ff_dim=64):
    """
    Build Transformer model.
    """
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(ff_dim))(inputs)
    attention_output = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=ff_dim)(x, x)
    x = tf.keras.layers.Add()([x, attention_output])
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    outputs = tf.keras.layers.Dense(1)(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

if __name__ == "__main__":
    ticker = 'AAPL'
    data = pd.read_csv(f'data/merged_data_with_features_{ticker}.csv')
    features = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']
    target = 'lastPrice'

    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data[features])

    # Prepare data
    time_steps = 60
    X_transformer, y_transformer = create_transformer_data(pd.DataFrame(data_scaled, columns=features), features, target='Close', time_steps=time_steps)

    # Split data
    split = int(0.8 * len(X_transformer))
    X_train, X_test = X_transformer[:split], X_transformer[split:]
    y_train, y_test = y_transformer[:split], y_transformer[split:]

    # Build and train model
    model = build_transformer_model((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

    # Save model
    model.save('models/transformer_option_pricing.h5')
