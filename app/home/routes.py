from flask import Blueprint, request, jsonify, g
from app.utils.decorators import auth_required, role_required
from firebase_admin import db
import logging

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/', methods=['GET'])
@auth_required
@role_required('farmer')
def home():
    """
    Home Dashboard Summary
    ---
    tags:
      - Home
    security:
      - BearerAuth: []
    responses:
      200:
        description: Successfully retrieved cow and milk data for the authenticated user
        schema:
          type: object
          properties:
            total_cows:
              type: integer
              example: 5
            total_milk_production:
              type: number
              format: float
              example: 63.5
      404:
        description: User data not found in the database
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
      401:
        description: Unauthorized or invalid token
        schema:
          type: object
          properties:
            error:
              type: string
              example: Unauthorized
    """
    user_id = g.user['uid']
    logging.info(f"User {user_id} accessed the home route.")

    user_ref = db.reference(f'users/{user_id}')
    user_data = user_ref.get()

    if not user_data or not isinstance(user_data, dict):
        logging.warning(f"User data not found for user {user_id}")
        return jsonify({'error': 'User not found'}), 404

    cows = user_data.get('cows', {})
    total_cows = 0
    total_milk = 0

    if isinstance(cows, dict):
        total_cows = len(cows)
        for cow_id, cow_data in cows.items():
            if isinstance(cow_data, dict):
                milk = cow_data.get('milk_production', 0)
                logging.info(f"Cow {cow_id}: milk_production = {milk} (type: {type(milk)})")
                if isinstance(milk, (int, float)):
                    total_milk += milk
                else:
                    logging.warning(f"Invalid milk_production value for cow {cow_id}: {milk}")
    elif isinstance(cows, list):
        total_cows = len([cow for cow in cows if cow is not None])
        for cow in cows:
            if isinstance(cow, dict):
                milk = cow.get('milk_production', 0)
                logging.info(f"Cow (list): milk_production = {milk} (type: {type(milk)})")
                if isinstance(milk, (int, float)):
                    total_milk += milk

    logging.info(f"User {user_id} has {total_cows} cows with total milk production: {total_milk}Litre")

    return jsonify({
        "total_cows": total_cows,
        "total_milk_production": total_milk
    }), 200
@home_bp.route('/healthsummary', methods=['GET'])
@auth_required
@role_required('farmer')
def get_farmer_cows_health_summary():
    try:
        user_id = g.user['uid']   
        logging.info(f"Fetching cow health summary for user: {user_id}")

        cows_ref = db.reference(f'users/{user_id}/cows')
        cows = cows_ref.get()

        if not cows:
            return jsonify({
                "total_healthy_cows": 0,
                "total_pregnant_cows": 0,
                "total_low_milk_cows": 0,
                "total_unhealthy_cows": 0
            }), 200


        healthy_count = 0
        pregnant_count = 0
        low_milk_count = 0
        unhealthy_count = 0

        for cow_id, cow_data in cows.items():
            status = cow_data.get('health_status', '').lower()

            if status == "healthy":
                healthy_count += 1
            elif status == "pregnant":
                pregnant_count += 1
            elif status in ["low milk", "low_milk"]:
                low_milk_count += 1
            elif status == "unhealthy":
                unhealthy_count += 1

        result = {
            "total_healthy_cows": healthy_count,
            "total_pregnant_cows": pregnant_count,
            "total_low_milk_cows": low_milk_count,
            "total_unhealthy_cows": unhealthy_count
        }
        logging.info(f"Cow health summary for user {user_id}: {result}")
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error fetching cow health summary for user: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


