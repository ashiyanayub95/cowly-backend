from functools import wraps
from flask import request, jsonify,g
from app.utils.auth_helper import generate_token ,verify_token
from firebase_admin import db
def auth_required(f):
    @wraps(f)
    def decorated_function(*args , **kwargs):
        token= request.headers.get('Authorization')
        if not token:
            return jsonify({'message':'Token is missing!'}), 401
        token = token.replace('Bearer ', '')

        user_data = verify_token(token)
        if not user_data:
            return jsonify({'message':'token is invalid!'}), 401
        g.user = user_data 

        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            token = token.replace('Bearer ', '')

            user_data = verify_token(token)
            if not user_data:
                return jsonify({'message': 'Token is invalid!'}), 401

            user_id = user_data['uid']
            role = db.reference(f'users/{user_id}/details/role').get()

            if role not in required_roles:
                return jsonify({'message': f'{", ".join(required_roles)} access required!'}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator


