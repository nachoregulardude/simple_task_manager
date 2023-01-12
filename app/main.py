#! /usr/bin/python3
from __future__ import annotations
from typing import List, Optional
from datetime import datetime

import typer
from rich.table import Table
from rich.console import Console

from app import (COLORS, INSERT_STMT, CONN, CUR)

APP = typer.Typer(help="Awesome CLI app for tracking tasks!")
CONSOLE = Console()


class Todo:

    def __init__(self,
                 task,
                 category,
                 date_added=None,
                 date_completed=None,
                 status=None,
                 position=None):
        self.task = ' '.join(word if word.isupper() else word.title()
                             for word in task.split(' '))
        self.category = category.upper()
        self.date_added = date_added or datetime.now()
        self.date_completed = date_completed or 'Not-Done'
        self.status = status or 1
        self.position = position

    def __repr__(self, ) -> str:
        return ' '.join(f"""{self.task}, {self.category}, {self.date_added},
                    {self.date_completed}, {self.status}, {self.position}""".
                        split())

    def get_dict(self) -> dict:
        """
        returns: dictionary of the task details
        """
        return {
            'task': self.task,
            'category': self.category,
            'date_added': self.date_added,
            'date_completed': self.date_completed,
            'status': self.status,
            'position': self.position
        }


@APP.command(short_help='adds an item. "task" "category"')
def add(task: str, category: str):
    typer.echo(f"Adding {task}, {category}")
    todo = Todo(task, category)
    insert_todo(todo)
    show(None)


@APP.command(short_help='''Deletes an item with position x.
    Delete entire task list if position is 0''')
def delete(position: int):
    if position == 0:
        typer.echo("Deleting the entire task list... 🤷")
    else:
        typer.echo(f"Deleting task at {position}")
    delete_todo(position - 1)
    show(None)


@APP.command(short_help='Update task at position x.')
def update(position: int,
           tasks: Optional[str] = typer.Argument(''),
           category: Optional[str] = typer.Argument('')):
    update_dict = {}
    if category:
        update_dict['category'] = category
    if tasks:
        update_dict['task'] = tasks
    typer.echo(f"Updating {position}!")
    update_todo(position - 1, update_dict)
    show(None)


@APP.command(short_help='mark a task as completed with position x')
def done(position: int):
    typer.echo(f"Task {position} marked as completed! 🙇")
    update_dict = {
        'status': 2,
        'position': position,
        'date_completed': datetime.now()
    }
    update_todo(position - 1, update_dict)
    show(None)


@APP.command(short_help='mark a task as working on with position x')
def working(position: int):
    typer.echo(f"Task {position} marked as ongoing!")
    update_dict = {
        'status': 3,
        'position': position,
    }
    update_todo(position - 1, update_dict)
    show(None)


@APP.command(short_help='''show the list of tasks in the table.
             Pass in a category to look at just that category''')
def show(categories: Optional[str] = typer.Argument('')):
    tasks = get_all_todos()
    table = Table(
        show_header=True,
        header_style="bold yellow4",
        title_justify='center',
        title='TASKS MANAGER 🐨',
    )
    table.add_column("#", style='dim', width=6)
    table.add_column("Tasks", min_width=20)
    table.add_column("Category", min_width=12, justify="right")
    table.add_column("Status", min_width=12, justify="right")
    table.add_column("Time Added", min_width=12, justify="right")
    table.add_column("Time Completed", min_width=12, justify="right")
    categories_to_search = categories.split(',') if categories else []

    all_done = check_if_all_done(tasks)
    map_dict = {
        1: '⭕ To Do',
        2: '✅ Done',
        3: '⌛ Progress',
    }
    for idx, task in enumerate(tasks, start=1):
        color = get_category_color(task.category)
        is_done_str = map_dict.get(task.status,
                                   'ERROR') if not all_done else '🍻'
        if categories_to_search and task.category.lower(
        ) not in categories_to_search:
            continue
        table.add_row(str(idx), task.task,
                      f"[{color}]{task.category}[/{color}]", is_done_str,
                      task.date_added.split('.')[0],
                      task.date_completed.split('.')[0])
    CONSOLE.print(table)


def get_category_color(category):
    return 'white' if category.lower() not in COLORS else COLORS[
        category.lower()]


def check_if_all_done(tasks):
    all_done = False
    if all(task.status == 2 for task in tasks) and tasks:
        CONSOLE.print('Nice! All tasks completed!🤌')
        all_done = True
    return all_done


def create_table():
    CUR.execute("""
                CREATE TABLE IF NOT EXISTS task_table (
                    task text,
                    category varchar,
                    date_added timestamp,
                    date_completed timestamp,
                    status smallint,
                    position smallint
                    )
                """)


def insert_todo(todo: Todo):
    CUR.execute('SELECT COUNT(*) FROM task_table')
    count = CUR.fetchone()[0]
    todo.position = count or 0
    with CONN:
        CUR.execute(INSERT_STMT, todo.get_dict())


def get_all_todos() -> List[Todo]:
    CUR.execute('SELECT * FROM task_table')
    return [Todo(*result) for result in CUR.fetchall()]


def delete_todo(position: int):
    if position == -1:
        with CONN:
            CUR.execute("DELETE FROM task_table")
        return
    CUR.execute("SELECT COUNT(*) FROM task_table")
    count = CUR.fetchone()[0]
    with CONN:
        CUR.execute("DELETE FROM task_table WHERE position = :position",
                    {"position": position})
        for pos in range(position + 1, count):
            change_position(pos, pos - 1, False)


def change_position(old_position: int,
                    new_position: int,
                    commit: bool = False):
    CUR.execute(
        'UPDATE task_table SET position = :new_pos WHERE position = :old_pos',
        {
            'old_pos': old_position,
            'new_pos': new_position
        })
    if commit:
        CONN.commit()


def update_todo(position: int, update_dict: dict):
    update_skl = ', '.join(f"{col} = :{col}" for col in update_dict)
    update_dict['position'] = position
    with CONN:
        CUR.execute(
            f'UPDATE task_table SET {update_skl} WHERE position = :position',
            update_dict)


def complete_todo(position: int, status: int):
    with CONN:
        CUR.execute(
            f"""UPDATE task_table SET status = {status}, date_completed =
            :date_completed WHERE position = :position""", {
                'position': position,
                'date_completed': datetime.now() if status == 2 else ''
            })


def main():
    create_table()
    typer.run(APP())


if __name__ == "__main__":
    raise SystemExit(main())
