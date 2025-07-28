from contextlib import contextmanager
import mysql.connector
import os
from budgetpet.logger import logger
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'secrets', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "budget"),
}


@contextmanager
def db_cursor():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        yield cursor
        connection.commit()
    except Exception as e:
        logger.error("Ошибка работы с базой данных: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()