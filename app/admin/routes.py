from flask import Blueprint, jsonify
from firebase_admin import db, auth
from app.utils.decorators import role_required
import logging

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    """
    Admin Dashboard
    ---
    tags:
      - Admin
    summary: Retrieve platform statistics for admin
    description: >
      This endpoint provides high-level statistics about the platform, including
      the total number of farmers and total number of cows registered.
      Requires an authenticated user with role = **admin**.
    security:
      - bearerAuth: []
    responses:
      200:
        description: Dashboard statistics retrieved successfully
        schema:
          type: object
          properties:
            total_cows:
              type: integer
              example: 27
            total_farmers:
              type: integer
              example: 10
      401:
        description: Unauthorized access (missing/invalid token or role not admin)
        schema:
          type: object
          properties:
            error:
              type: string
              example: Unauthorized
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
    """
    try:
        logging.info("Dashboard accessed by admin.")

        user_ref = db.reference('users')
        users = user_ref.get()
    
        total_cows = 0
        total_farmers = 0
        
        if users and isinstance(users, dict):
            for user_id, user_data in users.items():
                if not isinstance(user_data, dict):
                    continue

                details = user_data.get('details', {})
                if details and isinstance(details, dict) and details.get('role') == 'farmer':
                    total_farmers += 1

                cows = user_data.get('cows', {})
                if isinstance(cows, dict):
                    cow_count = len(cows)
                    total_cows += cow_count
                    logging.debug(f"Farmer {user_id} has {cow_count} cows.")
                elif isinstance(cows, list):
                    cow_count = len([cow for cow in cows if cow is not None])
                    total_cows += cow_count
                    logging.debug(f"Farmer {user_id} has {cow_count} cows (from list).")

        logging.info(f"Total Farmers: {total_farmers}, Total Cows: {total_cows}")

        return jsonify({
            'total_cows': total_cows,
            'total_farmers': total_farmers,
        }), 200

    except Exception as e:
        logging.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    
@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_user():
    try:
        logging.info("Admin requested all farmer users.")
        users_ref = db.reference('users')
        users = users_ref.get()

        if not users:
            logging.warning("No users found in the database.") 
            return jsonify({'message': 'No users found'}), 404 

        user_list = []
        for user_id, data in users.items():
            details = data.get('details', {})
            role = details.get('role')

            if role == 'farmer':
                user_list.append({
                    'user_id': user_id,
                    'email': details.get('email'),
                    'name': details.get('name'),
                    'role': role,
                })

        if not user_list:
            logging.warning("No farmer users found.")
            return jsonify({'message': 'No farmer users found'}), 404 

        return jsonify({'users': user_list}), 200

    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    
@admin_bp.route('/delete_user/<user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """
    Delete a User
    ---
    tags:
      - Admin
    summary: Delete a user by ID
    description: >
      Permanently deletes a user from both the Firebase Realtime Database and Firebase Authentication.  
      Only accessible by an **admin** user.
    security:
      - bearerAuth: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: Unique ID of the user to delete
        example: "L25krZy9Pza7vSIB7D0geMAaafa2"
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User L25krZy9Pza7vSIB7D0geMAaafa2 deleted successfully"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
      401:
        description: Unauthorized access (missing/invalid token or role not admin)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error"
    """
    try:
        logging.info(f"Admin attempting to delete user: {user_id}")

        user_ref = db.reference(f'users/{user_id}')
        if not user_ref.get():
            logging.warning(f"User {user_id} not found for deletion.")
            return jsonify({'error': 'User not found'}), 404
        
        user_ref.delete()
        logging.info(f"User {user_id} deleted successfully.")

        try:
            auth.delete_user(user_id)
            logging.info(f"Firebase user {user_id} deleted successfully.")
        except auth.UserNotFoundError:
            logging.warning(f"Firebase user {user_id} not found for deletion.")

        return jsonify({'message': f'User {user_id} deleted successfully'}), 200
    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500    

