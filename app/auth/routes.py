from flask import Blueprint, request, jsonify 
from firebase_admin import auth as firebase_auth, db
from app.utils.auth_helper import generate_token, verify_token
from werkzeug.security import generate_password_hash ,check_password_hash
import logging
import requests
import os 
from dotenv import load_dotenv
load_dotenv()

auth_bp = Blueprint('auth_bp', __name__,)
FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register New User
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - name
            - role
          properties:
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "MySecretPass123"
            name:
              type: string
              example: "John Doe"
            role:
              type: string
              example: "admin"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User registered successfully
            user_id:
              type: string
              example: abc123
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIs...
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing required fields
      409:
        description: Email already exists
        schema:
          type: object
          properties:
            error:
              type: string
              example: Email already exists
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal error occurred
    """

    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'name', 'role']
        if not all(field in data for field in required_fields):
            logging.warning("Register attempt with missing fields: %s", data)
            return jsonify({'error': 'Missing required fields'}), 400

        email = data['email']
        password = data['password']
        name = data['name']
        role = data.get('role', 'user')

        user = firebase_auth.create_user(email=email, password=password)
        db.reference(f'users/{user.uid}/details').set({
            'email': email,
            'name': name,
            'role': role,
            "password": generate_password_hash(password),
            'user_id': user.uid
        })

        logging.info(f"New user registered: {email} with role: {role}")
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.uid,
        }), 201

    except firebase_auth.EmailAlreadyExistsError:
        logging.warning(f"Register failed: Email already exists for {data.get('email')}")
        return jsonify({'error': 'Email already exists'}), 409

    except Exception as e:
        logging.exception("Unexpected error during registration")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIs...
            user_id:
              type: string
              example: U123456
            role:
              type: string
              example: admin
      400:
        description: Missing credentials or password not set
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing email or password
      401:
        description: Invalid login or password
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid login
            details:
              type: string
              example: Some backend exception message
    """

    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        logging.warning("Login attempt with missing credentials: %s", data)
        return jsonify({'error': 'Missing email or password'}), 400

    email = data['email']
    password = data['password']

    try:
        user = firebase_auth.get_user_by_email(email)
        u = db.reference(f'users/{user.uid}/details').get()
        stored_hashed_password = u.get('password')

        if not stored_hashed_password:
            logging.warning(f"Login failed: Password not set for {email}")
            return jsonify({'error': 'Password not set'}), 400

        if not check_password_hash(stored_hashed_password, password):
            logging.warning(f"Login failed: Invalid password for {email}")
            return jsonify({'error': 'Invalid password'}), 401

        token = generate_token(user.uid)
        logging.info(f"Login successful for user: {email}")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user.uid,
            'role': u.get('role'),   
        }), 200

    except Exception as e:
        logging.exception(f"Login failed for {email}")
        return jsonify({'error': 'Invalid login', 'details': str(e)}), 401
    
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Forgot Password
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: user@example.com
    responses:
      200:
        description: Password reset email sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password reset email sent successfully
      400:
        description: Email is missing from request
        schema:
          type: object
          properties:
            error:
              type: string
              example: Email is required
      500:
        description: Internal server error or Firebase error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Failed to send password reset email
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        logging.warning("Forgot password request with missing email")
        return jsonify({'error': 'Email is required'}), 400
    try:
        response = requests.post(
            f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}',
            json={
                'requestType': 'PASSWORD_RESET',
                'email': email
            }
        )

        if response.status_code == 200:
            logging.info(f"Password reset email sent to {email}")
            return jsonify({'message': 'Password reset email sent successfully'}), 200
            
        else:
            logging.error(f"Failed to send password reset email: {response.status_code} - {response.text}")
            return jsonify({'error': 'Failed to send password reset email'}), 500
        
    except Exception as e:
        logging.exception(f"Error in forgot password for {email}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500
         


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Successfully logged out. Please delete the token on client side.'}), 200






