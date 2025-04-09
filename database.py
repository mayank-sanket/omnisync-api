import psycopg2
import config

def get_db():
    conn = psycopg2.connect(config.DATABASE_URL)
    return conn

