import sqlite3
from datetime import datetime, timezone

from core.settings import DB_PATH
from core.log_conf import create_logger

"""Модуль для управления базой данных проекта."""

logger = create_logger(__name__, 'db.log')


def db_decorator(func):
    def db_wrapper(*args):
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            params = (cur, con) + args
            return func(*params)
        except Exception as e:
            logger.critical(f'DATABASE ERROR + {e}', exc_info=1)
            raise e
    return db_wrapper


@db_decorator
def create_db(*args):
    cur, con = args
    cur.execute('''CREATE TABLE IF NOT EXISTS empls(
                        id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        middle_name TEXT,
                        last_name TEXT NOT NULL,
                        job_pos TEXT NOT NULL,
                        avatar BLOB,
                        date_of TEXT NOT NULL,
                        time DATETIME
                    );
                ''')


if __name__ == '__main__':
    create_db()
