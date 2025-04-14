import psycopg2
import config



conn = psycopg2.connect(config.DATABASE_URL)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL
)
""")

conn.commit()

cursor.execute("""
               
CREATE TABLE IF NOT EXISTS account_session(
    id TEXT,
    email TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMPTZ, 
    FOREIGN KEY (id) REFERENCES accounts(id)
)
            
               """)


conn.commit()


# is wale table mein created_at, updated_at and expires_at (TIMESTAMPTZ) add kar do

# created_at to fix rahega, updated_at tab tab update hoga jab bhi refresh token ke through new access token generate hoga

# expires_at jaise hi complete hoga, refresh route hit hoga and uske baad : new access token aake store ho jaayega table mein alongwith the new expires_at value








# cursor.execute("""


# """)

# conn.commit()

conn.close()
