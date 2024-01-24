from environment import PG_URL
from config import db
import datetime
import psycopg

class PredictModel:
    @staticmethod
    def create(params):
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO predictions(top_one, image, confidence) VALUES(%s,%s,%s)", params=params)
            conn.commit()
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get():
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM predictions")
            conn.commit()
            predictions = cursor.fetchall()
            return predictions if predictions else None
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def save(params):
        try:
            prediction_name, file_url, prediction_conf, session_id = params
            data = {
                'user_id' : session_id,
                'top_one': prediction_name,
                'image': file_url,
                'confidence': prediction_conf,
                'created_at': datetime.datetime.now()
            }
            db.collection('predictions').add(data)
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
        finally:
            print("Saved")

    @staticmethod
    def get_data(user_id):
        try:
            return db.collection('predictions').where('user_id', '==', user_id).order_by('created_at').stream()
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
        finally:
            print("Saved")


class AuthModel:
    @staticmethod
    def login(params):
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM accounts WHERE username = %s AND password = %s", params=params)
            conn.commit()
            account = cursor.fetchone()
            return account if account else None
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def has_user(username):
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM accounts WHERE username = %s", [username])
            conn.commit()
            account = cursor.fetchone()
            return True if account else None
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def register(params=(None, None, None)):
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)", params)
            conn.commit()
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def profile(id):
        conn = psycopg.connect(PG_URL)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM accounts WHERE id = %s", (id))
            conn.commit()
            account = cursor.fetchone()
            return account if account else None
        except Exception as e:
            print(f"Something wen't wrong to database: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
