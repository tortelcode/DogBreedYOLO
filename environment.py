import os
from dotenv import load_dotenv
load_dotenv()

STORAGE_BUCKET=os.environ['storageBucket']
SERVICE=os.environ['CREDENTIALS']
PG_URL=os.environ['PG_URL']