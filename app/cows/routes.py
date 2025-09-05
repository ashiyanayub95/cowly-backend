from flask import Blueprint, request, jsonify,g
from firebase_admin import auth as firebase_auth, db
from app.utils.auth_helper import generate_token, verify_token
from datetime import datetime
import re
from app.utils.decorators import auth_required,role_required
import logging
cow_bp = Blueprint('cow_bp', __name__,)

@cow_bp.route('/addcow', methods=['POST'])
@auth_required
@role_required('farmer')
def add_cow():
    """
    Add a new cow to the farmer's profile
    ---
    tags:
      - Cows
    security:
      - bearerAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - cow_id
            - name
            - breed
            - age
            - health_status
            - milk_production
          properties:
            cow_id:
              type: string
              pattern: '^[a-zA-Z0-9_-]+$'
              example: cow_101
              description: Unique identifier for the cow (letters, numbers, underscores, hyphens).
            name:
              type: string
              example: Bessie
              description: Name of the cow.
            breed:
              type: string
              example: Holstein
              description: Breed of the cow.
            age:
              type: number
              example: 4
              description: Age of the cow in years.
            health_status:
              type: string
              example: Healthy
              description: Current health status of the cow.
            milk_production:
              type: number
              example: 20
              description: Average daily milk production in liters.
    responses:
      200:
        description: Cow added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Cow added successfully
      400:
        description: Bad request
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Missing Cow Data
    """
    user_id = g.user['uid']
    data = request.get_json()
    required_fields = ['cow_id', 'name', 'breed', 'age', 'health_status', 'milk_production']
    if not all(field in data for field in required_fields):
        logging.warning(f"Add cow failed: Missing fields in {data}")
        return jsonify({'Error': 'Missing Cow Data'}), 400
    
    cow_id = str(data['cow_id']).strip().lower()
    if not re.match(r'^[a-zA-Z0-9_-]+$', cow_id):
        logging.warning(f"Add cow failed: Invalid cow ID format '{cow_id}'")
        return jsonify({'Error': 'Invalid Cow ID format'}), 400
    
    existing = db.reference(f'users/{user_id}/cows/{cow_id}').get()
    if existing:
        logging.warning(f"Add cow failed: Cow ID '{cow_id}' already exists for user {user_id}")
        return jsonify({'Error': 'Cow ID already exists'}), 400
    
    created_at = datetime.utcnow().isoformat() + 'Z'
    cow_ref = db.reference(f'users/{user_id}/cows/{cow_id}')
    cow_ref.set({
        "cow_id": cow_id,
        "name": data['name'],
        "breed": data['breed'],
        "age": data['age'],
        "health_status": data['health_status'],
        "milk_production": data['milk_production'],
        "created_at": created_at,
    })
    logging.info(f"Cow '{cow_id}' added successfully for user {user_id}")
    return jsonify({'message': 'Cow added successfully'}), 200

@cow_bp.route('/getall', methods=['GET'])
@auth_required
@role_required('farmer')
def get_all_cows():
    """
    Get all cows for the authenticated farmer
    ---
    tags:
      - Cows
    security:
      - bearerAuth: []
    parameters: []
    responses:
      200:
        description: Successfully fetched all cows or no cows found
        schema:
          type: object
          properties:
            data:
              type: object
              additionalProperties:
                type: object
                properties:
                  cow_id:
                    type: string
                    example: cow_101
                  name:
                    type: string
                    example: Bessie
                  breed:
                    type: string
                    example: Holstein
                  age:
                    type: number
                    example: 4
                  health_status:
                    type: string
                    example: Healthy
                  milk_production:
                    type: number
                    example: 20
                  created_at:
                    type: string
                    example: 2025-08-14T10:00:00Z
            Error:
              type: string
              example: No cows found
      401:
        description: Unauthorized - token missing or invalid
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Authentication required
      403:
        description: Forbidden - user does not have the farmer role
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Access denied
    """
    user_id = g.user['uid']
    cow_ref = db.reference(f'users/{user_id}/cows')
    cow_data = cow_ref.get()

    if not cow_data:
        logging.info(f"No cows found for user {user_id}")
        return jsonify({'Error': 'No cows found'}), 200
    
    logging.info(f"All cows fetched for user {user_id}")
    return jsonify({'data': cow_data}), 200

@cow_bp.route('/update/<cow_id>', methods=['PATCH'])
@auth_required
@role_required('farmer')
def update_cow(cow_id):
    user_id = g.user['uid']
    data = request.get_json()
    allowed_fields = ['name', 'breed', 'age', 'health_status', 'milk_production']

    cow_ref = db.reference(f'users/{user_id}/cows/{cow_id}')
    current_cow_data = cow_ref.get()

    if not current_cow_data:
        logging.warning(f"Update failed: Cow '{cow_id}' not found for user {user_id}")
        return jsonify({'Error': 'Cow not found'}), 404

    update = {field: data[field] for field in allowed_fields if field in data}

    if update:
        update['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        cow_ref.update(update)
        logging.info(f"Cow '{cow_id}' updated for user {user_id} with: {update}")
        return jsonify({'message': 'Cow updated successfully'}), 200
    else:
        logging.warning(f"Update cow failed: No valid fields to update for cow '{cow_id}'")
        return jsonify({'error': 'No valid fields to update'}), 400

@cow_bp.route('/delete/<cow_id>', methods=['DELETE'])
@auth_required
@role_required('farmer')
def delete_cow(cow_id):
    """
    Delete a cow by its ID
    ---
    tags:
      - Cows
    security:
      - bearerAuth: []
    parameters:
      - name: cow_id
        in: path
        type: string
        required: true
        description: Unique identifier of the cow to delete.
        example: cow_101
    responses:
      200:
        description: Cow deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Cow cow_101 deleted successfully
      404:
        description: Cow not found
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Cow not found
      401:
        description: Unauthorized - token missing or invalid
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Authentication required
      403:
        description: Forbidden - user does not have the farmer role
        schema:
          type: object
          properties:
            Error:
              type: string
              example: Access denied
     """
    user_id = g.user['uid']
    cow_ref = db.reference(f'users/{user_id}/cows/{cow_id}')
    current_cow_data = cow_ref.get()

    if not current_cow_data:
        logging.warning(f"Delete cow failed: Cow '{cow_id}' not found for user {user_id}")
        return jsonify({'Error': 'Cow not found'}), 404

    cow_ref.delete()
    logging.info(f"Cow '{cow_id}' deleted for user {user_id}")
    return jsonify({'message': f'Cow {cow_id} deleted successfully'}), 200

@cow_bp.route('/search', methods=['GET'])
@auth_required
@role_required('farmer')
def search_cows():
    user_id = g.user['uid']
    field = request.args.get('field')
    value = request.args.get('value')

    if not field or not value:
        logging.warning(f"Search cows failed: Missing field/value. Field: {field}, Value: {value}")
        return jsonify({'Error': 'Missing search field or value'}), 400

    cows_ref = db.reference(f'users/{user_id}/cows')
    cows = cows_ref.get()

    if not cows:
        logging.info(f"Search cows: No cows found for user {user_id}")
        return jsonify({'message': 'No cows found'}), 404

    matching_cows = []
    for cow_id, cow_data in cows.items():
        if field in cow_data and str(cow_data[field]).lower() == value.lower():
            matching_cows.append({**cow_data, 'cow_id': cow_id})

    logging.info(f"Search cows: Found {len(matching_cows)} matches for user {user_id}, field='{field}', value='{value}'")
    return jsonify({'results': matching_cows}), 200

@cow_bp.route('/<cow_id>/profile', methods=['GET'])
@auth_required
@role_required('farmer')
def cow_profile(cow_id):
    """
    Get Cow Profile
    ---
    tags:
      - Cows
    summary: Fetch the latest health and activity profile of a cow
    description: >
      This endpoint retrieves the latest temperature and calculates the activity level 
      (Low, Medium, High) of a cow based on accelerometer and gyroscope readings 
      stored in Firebase. Only farmers can access this endpoint.
    parameters:
      - name: cow_id
        in: path
        required: true
        description: The unique identifier of the cow
        schema:
          type: string
    responses:
      200:
        description: Successfully retrieved the cow profile
        content:
          application/json:
            example:
              cow_id: "cow123"
              temperature: 38.5
              activity_level: "High"
      400:
        description: Invalid or incomplete data in the latest reading
        content:
          application/json:
            example:
              Error: "Invalid reading format. Expected dict, got string"
      404:
        description: No readings found for this cow
        content:
          application/json:
            example:
              Error: "No readings found for this cow"
      401:
        description: Unauthorized (missing or invalid token)
      403:
        description: Forbidden (user does not have farmer role)
    security:
      - bearerAuth: []
    """
    user_id = g.user['uid']

    readings_ref = db.reference(f'users/{user_id}/cows/{cow_id}/readings')
    readings_data = readings_ref.get()

    if not readings_data:
        return jsonify({'Error': 'No readings found for this cow'}), 404

    # Get the latest reading entry (assuming readings are timestamp-keyed)
    latest_timestamp = max(readings_data.keys())
    latest_data = readings_data[latest_timestamp]

    if not isinstance(latest_data, dict):
        return jsonify({'Error': 'Invalid reading format. Expected dict, got string'}), 400

    temperature = latest_data.get('temperature')
    accel = latest_data.get('accelerometer')
    gyro = latest_data.get('gyroscope')

    if temperature is None or accel is None or gyro is None:
        return jsonify({'Error': 'Incomplete reading data'}), 400

    accel_magnitude = (accel['x']**2 + accel['y']**2 + accel['z']**2) ** 0.5
    gyro_magnitude = (gyro['x']**2 + gyro['y']**2 + gyro['z']**2) ** 0.5

    ACCEL_THRESHOLD = 1.5
    GYRO_THRESHOLD = 0.8

    if accel_magnitude > ACCEL_THRESHOLD or gyro_magnitude > GYRO_THRESHOLD:
        activity_level = "High"
    elif accel_magnitude > (ACCEL_THRESHOLD * 0.5) or gyro_magnitude > (GYRO_THRESHOLD * 0.5):
        activity_level = "Medium"
    else:
        activity_level = "Low"

    profile = {
        'cow_id': cow_id,
        'temperature': temperature,
        'activity_level': activity_level
    }

    logging.info(f"Cow profile fetched for '{cow_id}' by user {user_id}")
    return jsonify(profile), 200
