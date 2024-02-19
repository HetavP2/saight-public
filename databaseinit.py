import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "",
})

ref = db.reference("user")


data = {"777023": {"name": "Hetav Patel", "phone_number": 17486489543, "birth_date": "2007", "email": "patelski@gmail.com", "relation": "friend", "last_seen": "2024-01-13 11:57:34", "times_seen": 5}}

for key, value in data.items():
    ref.child(key).set(value)