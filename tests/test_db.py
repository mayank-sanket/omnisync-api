import pytest
from database import get_db
from psycopg2 import OperationalError

@pytest.fixture
def db_connection():
    """Fixture to handle database connection and cleanup"""
    try:
        conn = get_db()
        yield conn
    finally:
        if conn:
            conn.close()

@pytest.fixture
def db_cursor(db_connection):
    """Fixture to handle cursor and cleanup"""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()

def test_postgres_connection(db_cursor):
    """Test database connectivity"""
    try:
        db_cursor.execute("SELECT 1;")
        result = db_cursor.fetchone()
        assert result[0] == 1
    except OperationalError as e:
        pytest.fail(f"Could not connect to the PostgreSQL database: {e}")

def test_write_functionality(db_cursor):
    try:
        db_cursor.execute(""" CREATE TABLE test_table (
                          id SERIAL PRIMARY KEY, 
                          name VARCHAR(50))""")
        db_connection.commit()
        db_cursor.execute("""
        INSERT INTO test_table(name) VALUES ('test value')
        RETURNING id;
""")
        db_connection.commit()
        result = db_cursor.fetchone()


        assert result is not None
        assert result[0] > 0
    except OperationalError as e:
        pytest.fail(f"Could not write to the database: {e}")
    
    finally:
        db_cursor.execute("DROP TABLE IF EXISTS test_table")
        db_connection.commit()