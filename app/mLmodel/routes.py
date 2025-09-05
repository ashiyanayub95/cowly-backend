from flask import Blueprint, request, jsonify, g
from app.utils.decorators import auth_required
from app.mLmodel.milk_prediction_model import predict_milk_yield
import logging

predict_bp = Blueprint('predict_bp', __name__)

@predict_bp.route('/milk', methods=['POST'])
@auth_required
def predict():
    """
    Predict Milk Yield
    ---
    tags:
      - Predictions
    summary: Predict the expected milk yield of a cow
    description: >
      This endpoint accepts cow-related input features and predicts the expected 
      milk yield (in litres) using a trained machine learning model. 
      Only authenticated users can access this endpoint.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              age:
                type: number
                example: 4
              breed:
                type: string
                example: "Holstein Friesian"
              health_status:
                type: string
                example: "Healthy"
              feed_intake:
                type: number
                description: Daily feed intake in kilograms
                example: 25.5
              lactation_stage:
                type: string
                example: "Mid"
            required:
              - age
              - weight
              - feed_intake
              - temperature
    responses:
      200:
        description: Successfully predicted the milk yield
        content:
          application/json:
            example:
              predicted_milk_yield: "22.45 litres"
      400:
        description: Invalid request or prediction error
        content:
          application/json:
            example:
              error: "Missing required field: feed_intake"
      401:
        description: Unauthorized (missing or invalid token)
    security:
      - bearerAuth: []
    """
    user_id = g.user['uid']
    try:
        data = request.get_json()
        logging.info(f"User {user_id} sent data for prediction: {data}")
        
        prediction = predict_milk_yield(data)
        logging.info(f"Prediction result for user {user_id}: {prediction:.2f} ")

        return jsonify({
            'predicted_milk_yield': round(prediction, 2),
            'unit': 'litres'
        }), 200
            
    
    except Exception as e:
        logging.error(f"Error in prediction for user {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 400
