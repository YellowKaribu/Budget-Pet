from contextlib import contextmanager
import mysql.connector
import os
from dotenv import load_dotenv
from budgetpet.infrastructure.logging.logger import logger


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..','..','..', 'secrets', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "budget"),
}

@contextmanager
def get_db_cursor():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error("DB error: %s", e)
        raise
    finally:
        cursor.close()
        connection.close()

