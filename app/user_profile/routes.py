from flask import Blueprint,request,jsonify,g
from firebase_admin import auth as firebase_auth, db
from app.utils.auth_helper import generate_token, verify_token
from datetime import datetime
from app.utils.decorators import auth_required ,role_required
import logging
user_bp = Blueprint('user', __name__)
@user_bp.route('/profile', methods=['GET'])
@auth_required
@role_required(['farmer'])
def get_user_profile():
    """
    Get User Profile
    ---
    tags:
      - Auth
    summary: Retrieve the authenticated user's profile
    description: Returns profile information such as name, email, role, and user ID for the currently authenticated user.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          type: object
          properties:
            profile:
              type: object
              properties:
                name:
                  type: string
                  example: John Doe
                email:
                  type: string
                  example: john@example.com
                role:
                  type: string
                  example: farmer
                user_id:
                  type: string
                  example: abc123uid
      404:
        description: User profile not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
      500:
        description: Server error during profile retrieval
        schema:
          type: object
          properties:
            error:
              type: string
              example: Failed to fetch profile
    """
    user_id = g.user['uid']
    logging.info(f"Fetching profile for user_id: {user_id}")

    try:
        user_ref = db.reference(f'users/{user_id}/details')
        user_profile = user_ref.get()

        if not user_profile:
            logging.warning(f"User profile not found for user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        profile_data = {
            'name': user_profile.get('name'),
            'email': user_profile.get('email'),
            'role': user_profile.get('role'),
            'user_id': user_profile.get('user_id')
        }

        logging.info(f"Profile fetched successfully for user_id: {user_id}")
        return jsonify({'profile': profile_data}), 200

    except Exception as e:
        logging.error(f"Error fetching profile for user_id {user_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch profile'}), 500

@user_bp.route('/update', methods=['PUT'])
@auth_required
def update_user_profile():
    try:
        user_id = g.user['uid']
        logging.info(f"Received profile update request for user_id: {user_id}")
        
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data:
            logging.warning(f"Invalid input data for user_id: {user_id} | Data: {data}")
            return jsonify({'error': 'Invalid input data'}), 400

        user_ref = db.reference(f'users/{user_id}/details')
        if not user_ref.get():
            logging.warning(f"User not found during profile update | user_id: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        user_ref.update(data)
        logging.info(f"Profile updated successfully for user_id: {user_id}")
        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        logging.error(f"Error updating profile for user_id: {user_id} | Error: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while updating profile'}), 500