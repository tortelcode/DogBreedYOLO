# Setup and Installation

[Requirements](#requirements)

[Setup](#setup)

[Installation](#installation)

[Usage](#usage)

[Note](#note)

[Update](#update)

[How it works](#how-it-works)

## Requirements

Python 3.9 and up

PostgreSQL

Firebase

## Setup

Clone the repository or Download the zip

```bash
git clone https://github.com/tortelcode/DogBreedYOLO.git
```

Extract the folder (if you downloaded)

Then run the ff. command in any terminal on your pc

```bash
cd DogBreedYOLO
```

## Installation

1. Go to directory DogBreedYOLO.

2. Open your terminal and go to your project directory

and run the command below to install required dependecies

```bash
pip install -r requirements.txt
```

3. Run ths ff. command in the root directory of project

Run as production mode

```bash
flask run
```

Run as Development mode, also track the changes in code

```bash
flask run --debug
```

## Usage

Go to your browser and type the url below

```bash
http://localhost:5000
```

or

```bash
http://127.0.0.1:5000
```

### Routes available

To navigate page, make sure your localhost + path is correct

Login (unauthenticated) or Homepage (authenticated only)

```bash
/
```

Profile

```bash
/profile
```

Prediction History

```bash
/predictions
```

API to get prediction history data (authenticated)

```bash
/api/get-predictions
```

# Integration

## Databases

PostgreSQL

Firebase

# Note

You can freely use database to your external projects to explore.

The .env and credentials.json file are both credentials, you can freely use these until january 2024.

# Update

To update your current branch, go your project directory and enter this command on your terminal

```bash
git pull
```

Make sure always run the command below before you run, otherwise you may encountered an error.

```bash
pip install -r requirements.txt
```

# How it works

## Database Setup

Using ```psycopg``` library, you can connect your ```PostgreSQL``` database in Python

Here's how it works

This is the basic to connect database in python

```python
from environment import PG_URL # another py script
import psycopg # library for PostgreSQL

conn = psycopg.connect(PG_URL) # Initialize connection
cursor = conn.cursor() # Interact to database
cursor.execute(SQL) # Execute Query
cursor.commit() # To make changes
```

```environment``` module is a python file contains ```PG_URL``` and import it from other py script

PG_URL is an environment variable used as ```Connection String``` to be able to access the ```Database```

You can see the variable ```PG_URL``` inside ```.env``` file

```PG_URL``` variable in ```.env``` file is a ```Connection String``` where ```PostgreSQL``` connection store this securely

it means no one can view or edit the ```.env``` file in the client.

```conn``` is assigned variable to initialize and open the connection to ```PostgreSQL``` Database

```cursor``` is used to interact with the database by executing ```sql``` query.

```execute``` function used to validate and execute your ```sql``` command

```commit``` is used if you want to store the data to database.

this will work only if you had data that needs to save in the database.

```python
from environment import SERVICE, STORAGE_BUCKET
import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate(SERVICE)
app = firebase_admin.initialize_app(cred, {
    'storageBucket' : STORAGE_BUCKET
})
db = firestore.client()
bucket = storage.bucket(app=app)
```

same as above, this is the code to initialize database

```cred``` variable used to attach the credential of ```Firebase``` to allow us to connect with their cloud service.

Basically, to authorized our application.

```app``` is variable represent as our connection

```db``` is to connect to the ```Firebase firestore```

```firestore``` is a database from ```Firebase```

```bucket``` is a document object to store files in the cloud and also get the file.
