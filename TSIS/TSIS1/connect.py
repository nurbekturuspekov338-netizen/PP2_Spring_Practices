import psycopg2
from config import DB_host, DB_base, DB_user, DB_pass
 
 
def get_connection():
    """Open and return a new psycopg2 connection with autocommit off."""
    conn = psycopg2.connect(
        host=DB_host,
        database=DB_base,
        user=DB_user,
        password=DB_pass
    )
    conn.autocommit = False
    return conn
 
 
def get_cursor(conn):
    """Return a cursor from an existing connection."""
    return conn.cursor()
 
 
def close(conn, cur=None):
    """Safely close cursor and connection."""
    if cur:
        try:
            cur.close()
        except Exception:
            pass
    if conn:
        try:
            conn.close()
        except Exception:
            pass