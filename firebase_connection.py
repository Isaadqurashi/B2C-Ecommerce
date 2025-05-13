import firebase_admin
from firebase_admin import db, credentials

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kuchu-muchu-default-rtdb.firebaseio.com/'
})


# refrence to the root of the database
ref = db.reference('/')
ref.get() #retrieving the data from the root of the database

db.reference('/name').get()
db.reference('/videos').set(3)
ref.get()

db.reference('/').update({'language': 'python'})
ref.get()

db.reference('/').update({'subscribed': True})
ref.get()

db.reference('/titles').push().set('create modern ui in python')
ref.get()

def increment_transaction(current_val):
    return current_val +1

db.reference('/title_count').transaction(increment_transaction)
ref.get()

db.reference('language').delete()
ref.get()