import jwt
import datetime
from dotenv import load_dotenv
import os
import logging

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def generate_token(uid):
    try:
        payload = {
            'uid': uid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        logging.info(f"Token generated for user_id: {uid}")
        return token
    except Exception as e:
        logging.error(f"Failed to generate token for user_id: {uid} | Error: {str(e)}", exc_info=True)
        raise

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        logging.info(f"Token verified successfully for user_id: {decoded.get('uid')}")
        return decoded
    except jwt.ExpiredSignatureError as e:
        logging.warning("Token verification failed: Token has expired.")
        raise jwt.ExpiredSignatureError("Token has expired.")
    except jwt.InvalidTokenError as e:
        logging.warning("Token verification failed: Invalid token.")
        raise jwt.InvalidTokenError("Invalid token.")
    except Exception as e:
        logging.error(f"Unexpected error during token verification | Error: {str(e)}", exc_info=True)
        raise