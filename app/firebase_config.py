import firebase_admin
from firebase_admin import credentials , db

cred =credentials.Certificate("jsonkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' :'https://flask-16046-default-rtdb.firebaseio.com/'
})