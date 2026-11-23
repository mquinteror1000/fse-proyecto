import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database="estacionamiento",
        user="fse",
        password=os.getenv("DB_PASS", "EMBEBIDOS@2026.,"),
        cursor_factory=RealDictCursor
    )
