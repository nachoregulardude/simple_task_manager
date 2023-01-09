import sqlite3
from os.path import exists, expanduser
from os import mkdir

COLORS = {
    'priority': 'red1',
    'teal': 'bright_cyan',
    'learn': 'dark_sea_green4',
    'ideas': 'dark_olive_green2',
    'reminders': 'orange_red1',
    'study': 'navajo_white1',
}
INSERT_STMT = """INSERT INTO task_table VALUES
(:task, :category, :date_added, :date_completed, :status, :position)"""
HOME_DIR = expanduser('~')
DB_PATH = f'{HOME_DIR}/.config/task_tracker'
if not exists(DB_PATH):
    print('')
    mkdir(DB_PATH)
CONN = sqlite3.connect(f"{DB_PATH}/task_list.db")
CUR = CONN.cursor()
