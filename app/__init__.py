import sqlite3
from os.path import exists, expanduser
from os import mkdir

COLORS = {
    'priority': 'red1',
    'teal': 'dark_cyan',
    'learn': 'dark_sea_green4',
    'ideas': 'dark_olive_green2',
    'reminders': 'orange_red1',
    'study': 'navajo_white1',
}

COLORS_TUP = ('bright_red', 'green', 'yellow', 'bright_magenta',
              'dodger_blue4', 'green3', 'dark', 'spring_green3', 'purple4',
              'medium_turquoise', 'deep_pink4h')
INSERT_STMT = """INSERT INTO task_table VALUES
(:task, :category, :date_added, :date_completed, :status, :position)"""
HOME_DIR = expanduser('~')
DB_PATH = f'{HOME_DIR}/.config/task_tracker'
if not exists(DB_PATH):
    mkdir(DB_PATH)
CONN = sqlite3.connect(f"{DB_PATH}/task_list.db")
CUR = CONN.cursor()
