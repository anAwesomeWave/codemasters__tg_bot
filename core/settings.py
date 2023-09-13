import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = BASE_DIR + '/employees.db'
EXPECTED_VALUES = ('first_name', 'last_name', 'job_pos', 'project')
ALL_DB_COLUMNS = (
    'ID', 'first_name',
    'middle_name', 'last_name',
    'job_pos', 'project',
    'avatar', 'time'
)