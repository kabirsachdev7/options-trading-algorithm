# backend/models/train_fnn_strategy.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import os

# Configuration
DATA_PATH = "../data/merged_data_with_features_AAPL.csv"  # Update as needed
MODEL_SAVE_PATH = "fnn_strategy.keras"
FEATURES = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility']
TARGET = 'Strategy'  # This should be a column in your dataset indicating the strategy

def load_data():
    data = pd.read_csv(DATA_PATH)
    data = data.sort_values('Date')  # Ensure data is sorted by date
    return data

def preprocess_data(data):
    # Encode the target variable
    label_encoder = LabelEncoder()
    data['Strategy_Encoded'] = label_encoder.fit_transform(data[TARGET])
    
    # Features and target
    X = data[FEATURES]
    y = data['Strategy_Encoded']
    
    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, label_encoder

def build_model(input_dim, num_classes):
    model = Sequential()
    model.add(Dense(128, input_dim=input_dim, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model():
    data = load_data()
    X, y, scaler, label_encoder = preprocess_data(data)
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    num_classes = len(label_encoder.classes_)
    input_dim = X_train.shape[1]
    
    model = build_model(input_dim, num_classes)
    
    early_stop = EarlyStopping(monitor='val_loss', patience=10)
    
    history = model.fit(
        X_train, y_train,
        batch_size=32,
        epochs=100,
        validation_data=(X_test, y_test),
        callbacks=[early_stop]
    )
    
    # Save the model
    model.save(MODEL_SAVE_PATH)
    print(f"FNN Strategy Model saved to {MODEL_SAVE_PATH}")
    
    # Save the scaler and label encoder for future use
    import joblib
    joblib.dump(scaler, "fnn_scaler.pkl")
    joblib.dump(label_encoder, "fnn_label_encoder.pkl")
    print("Scaler and Label Encoder saved.")

if __name__ == "__main__":
    train_model()
