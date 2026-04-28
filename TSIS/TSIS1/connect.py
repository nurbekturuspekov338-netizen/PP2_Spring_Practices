import psycopg2
from config import DB_host, DB_base, DB_user, DB_pass


def connect():
    return psycopg2.connect(
        host=DB_host,
        dbname=DB_base,
        user=DB_user,
        password=DB_pass
        )