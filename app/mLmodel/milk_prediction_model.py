
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
import os
from tensorflow.keras.models import load_model # type: ignore


model_path = os.path.join(os.path.dirname(__file__), 'milk_yield_hybrid_model.h5')
model = load_model(model_path, compile=False)
scaler_path = os.path.join(os.path.dirname(__file__), 'minmax_scaler.pkl')
scaler = joblib.load(scaler_path)

def predict_milk_yield(input_data):
    # Convert input data to DataFrame
    df_input = pd.DataFrame([input_data])
    df_input['milk_yield'] = 0

    # Scale the input data
    scaled_input = scaler.transform(df_input)
    scaled_sequence = scaled_input[:, :-1]
    X_single = np.expand_dims(scaled_sequence, axis=0)

    # Predict the milk yield
    predicted_scaled = model.predict(X_single)
    reconstructed = np.concatenate([scaled_sequence[-1].reshape(1, -1), predicted_scaled], axis=1)
    predicted_milk_yield = scaler.inverse_transform(reconstructed)[0, -1]

    return predicted_milk_yield
