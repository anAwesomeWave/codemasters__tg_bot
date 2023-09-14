import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = BASE_DIR + '/employees.db'
EXPECTED_VALUES = ('first_name', 'last_name', 'job_pos', 'project', 'time')
ALL_DB_COLUMNS = (
    'ID', 'first_name',
    'middle_name', 'last_name',
    'job_pos', 'project',
    'avatar', 'time'

)
BASIC_BOT_COMMANDS = ('/start', '/add_employee', '/update_employee', '/find_by_id', '/get_employees')