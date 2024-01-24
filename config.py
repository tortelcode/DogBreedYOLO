from environment import SERVICE, STORAGE_BUCKET
import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate(SERVICE)
app = firebase_admin.initialize_app(cred, {
    'storageBucket' : STORAGE_BUCKET
})
db = firestore.client()
bucket = storage.bucket(app=app)