import json
import numpy as np
import pandas as pd
import tensorflow as tf
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "../models")

NUMERIC_COLS = [
    "Age", "Milk_Production_Liters", "Temperature_C",
    "Heart_Rate_BPM", "Respiratory_Rate_BPM",
    "Appetite_Score", "Mobility_Score"
]

class CowDiseaseTFLite:
    def __init__(self):
        self.interpreter = tf.lite.Interpreter(model_path=os.path.join(BASE_DIR, "cow_lstm.tflite"))
        self.interpreter.allocate_tensors()
        self.inp = self.interpreter.get_input_details()[0]
        self.out = self.interpreter.get_output_details()[0]
        self.labels = self._load_label_map()

        # load preprocessing
        with open(os.path.join(BASE_DIR, "preprocessing_params.json"), "r") as f:
            self.prep_params = json.load(f)
        with open(os.path.join(BASE_DIR, "feature_order.json"), "r") as f:
            self.feature_order = json.load(f)

    def _load_label_map(self):
        with open(os.path.join(BASE_DIR, "label_mapping.json"), "r") as f:
            lm = json.load(f)
        return {str(k): v for k, v in lm.items()}

    def _preprocess(self, sample: dict):
        df = pd.DataFrame([sample])

        # Handle categorical
        if "Breed" in df.columns:
            df = pd.get_dummies(df, columns=["Breed"], drop_first=True)

        # Normalize numeric columns
        for col in NUMERIC_COLS:
            if col in df.columns:
                mean = self.prep_params["means"].get(col, 0.0)
                std = self.prep_params["stds"].get(col, 1.0) or 1.0
                df[col] = (df[col].astype(float) - mean) / std

        # Reorder
        df = df.reindex(columns=self.feature_order, fill_value=0)
        x = df.to_numpy(dtype=np.float32).reshape(1, 1, len(self.feature_order))
        return x

    def predict(self, sample: dict) -> str:
        x = self._preprocess(sample)
        self.interpreter.set_tensor(self.inp['index'], x)
        self.interpreter.invoke()
        probs = self.interpreter.get_tensor(self.out['index'])[0]
        top_idx = int(np.argmax(probs))
        return self.labels.get(str(top_idx), f"class_{top_idx}")
