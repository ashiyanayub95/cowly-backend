from flask import Flask, request, jsonify ,g
from .disease import CowDiseaseTFLite
from flask import Blueprint
import logging
from app.utils.decorators import auth_required 
from app.utils.decorators import role_required


pred_bp = Blueprint('pred_bp', __name__)
model = CowDiseaseTFLite()  # load once at startup

@pred_bp.route("/disease", methods=["POST"])
@auth_required
@role_required('farmer')
def predict_disease():
    user_id = g.user['uid']
    try:
        data = request.get_json()
        data["isolated"] = 0 if data["isolated"] == "Yes" else 1
        # Validate input fields
        required = ["Age","Breed","Milk_Production_Liters","Temperature_C",
                    "Heart_Rate_BPM","Respiratory_Rate_BPM",
                    "Appetite_Score","Mobility_Score","isolated",]
        
        for r in required:
            if r not in data:
                return jsonify({"error": f"Missing field: {r}"}), 400

        prediction = model.predict(data)
        logging.info(f"Prediction: {prediction} for input: {data}")
        return jsonify({"prediction": prediction}), 200

    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500


