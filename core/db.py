import sqlite3
from datetime import datetime, timezone

from core.settings import DB_PATH, EXPECTED_VALUES
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
                        project TEXT NOT NULL,
                        avatar BLOB,
                        time DATETIME
                    );
                ''')


@db_decorator
def add_employee(*args):
    """Добавление нового работника в буазу данных.
        (пока условимся, что будут передаваться только те данные,
        которые необхдимы
        В случае успеха возвращает id добавленного работника
    """
    try:
        cur, con, data = args
    except ValueError:
        logger.error(f"Cannot add user, not enough args {args}", exc_info=1)
        return None
    not_passed = []
    try:
        for arg in EXPECTED_VALUES:
            if arg not in data:
                not_passed.append(arg)
        if len(not_passed) != 0:
            raise KeyError(f'Required args was not passed {not_passed}')
    except KeyError as e:
        logger.error(e)
        return None
    arg_names = list(data.keys())
    values = [data[x] for x in arg_names]
    cur.execute(
        "INSERT INTO empls(first_name, last_name, job_pos, project, time) "
        "VALUES(?, ?, ?, ?, ?)",
        values
    )
    id_of_added_employee = cur.lastrowid
    con.commit()
    return id_of_added_employee
    # можно передать словарь например, и в insert (передать *d.keys())


@db_decorator
def get_user_by_id(*args):
    try:
        cur, con, emp_id = args
    except ValueError:
        logger.error(f"Cannot add user, not enough args {args}", exc_info=1)
        return None
    try:
        cur.execute("SELECT * FROM empls WHERE id=?", (emp_id,))
    except sqlite3.OperationalError as e:
        logger.error(f'Cannot retrieve user. {e}', exc_info=1)
        return None
    return cur.fetchone()


@db_decorator
def update_field(*args):
    ''' изменение поля
        прнимает id, и field -> {k: updated_val}
    '''
    try:
        cur, con, emp_id, field = args
    except ValueError:
        logger.error(f"Cannot add user, not enough args {args}", exc_info=1)
        return None
    updated_item = list(list(field.items())[0])
    if updated_item[0] == 'avatar':
        updated_item[1] = sqlite3.Binary(updated_item[1])
    query = "UPDATE empls SET (" + updated_item[0] + ") =? WHERE ID=?"
    cur.execute(query, (updated_item[1],emp_id))
    con.commit()

    return 0


@db_decorator
def find_employer_by_fields(*args):
    try:
        cur, con, key, val = args
        query = (f"SELECT id, first_name, middle_name, last_name, job_pos, "
                f"project FROM empls WHERE " + key + " LIKE ? COLLATE NOCASE")
        cur.execute(query, (val,))
        ans = cur.fetchall()
        return ans
    except ValueError:
        logger.error(f"Cannot add user, not enough args {args}", exc_info=1)
        return None


if __name__ == '__main__':
    print(get_user_by_id(1))
