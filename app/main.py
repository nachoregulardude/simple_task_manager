#! /usr/bin/python3
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
        self.task = task.title()
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


@APP.command(short_help='adds an item')
def add(task: str, category: str):
    typer.echo(f"Adding {task}, {category}")
    todo = Todo(task, category)
    insert_todo(todo)
    show(None)


@APP.command(
    short_help=
    'deletes an item with position x. Delete entire task list if position is 0'
)
def delete(position: int):
    if position == 0:
        typer.echo("Deleting the entire task list... 🤷")
        delete_todo(-1)
        show(None)
        return
    typer.echo(f"Deleting {position}")
    delete_todo(position - 1)
    show(None)


@APP.command()
def update(position: int, category: str, tasks: str):
    update_dict = {}
    if category:
        update_dict['category'] = category
    if tasks:
        update_dict['task'] = tasks
    typer.echo(f"Updating {position}!")
    update_todo(position - 1, update_dict)
    show(None)


@APP.command(short_help='mark an item as completed with position x')
def done(position: int):
    typer.echo(f"Task {position} marked as completed! 🙇")
    complete_todo(position - 1)
    show(None)


@APP.command(short_help='show the list of tasks in the table')
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
    categories_to_search = []
    if categories:
        categories_to_search = categories.split(',')

    def get_category_color(category):
        return 'white' if category.lower() not in COLORS else COLORS[
            category.lower()]

    all_done = False
    if all(task.status == 2 for task in tasks) and tasks:
        CONSOLE.print('Nice! All tasks completed!🤌')
        all_done = True

    for idx, task in enumerate(tasks, start=1):
        color = get_category_color(task.category)
        if not all_done:
            is_done_str = '✅ Done' if task.status == 2 else '⭕ To Do'
        else:
            is_done_str = '🍻 All done!'
        if categories_to_search and task.category.lower(
        ) not in categories_to_search:
            continue
        table.add_row(str(idx), task.task,
                      f"[{color}]{task.category}[/{color}]", is_done_str,
                      task.date_added.split('.')[0],
                      task.date_completed.split('.')[0])
    CONSOLE.print(table)


def create_table():
    CUR.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    task text,
                    category varchar,
                    date_added timestamp,
                    date_completed timestamp,
                    status smallint,
                    position smallint
                    )
                """)


def insert_todo(todo: Todo):
    CUR.execute('SELECT COUNT(*) FROM todos')
    count = CUR.fetchone()[0]
    todo.position = count or 0
    with CONN:
        CUR.execute(INSERT_STMT, todo.get_dict())


def get_all_todos() -> List[Todo]:
    CUR.execute('SELECT * FROM todos')
    return [Todo(*result) for result in CUR.fetchall()]


def delete_todo(position: int):
    if position == -1:
        with CONN:
            CUR.execute("DELETE FROM todos")
        return
    CUR.execute("SELECT COUNT(*) FROM todos")
    count = CUR.fetchone()[0]
    with CONN:
        CUR.execute("DELETE FROM todos WHERE position = :position",
                    {"position": position})
        for pos in range(position + 1, count):
            change_position(pos, pos - 1, False)


def change_position(old_position: int,
                    new_position: int,
                    commit: bool = False):
    CUR.execute(
        'UPDATE todos SET position = :new_pos WHERE position = :old_pos', {
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
            f'UPDATE todos SET {update_skl} WHERE position = :position',
            update_dict)


def complete_todo(position: int):
    with CONN:
        CUR.execute(
            "UPDATE todos SET status = 2, date_completed = :date_completed WHERE position = :position",
            {
                'position': position,
                'date_completed': datetime.now()
            })


def main():
    create_table()
    typer.run(APP())


if __name__ == "__main__":
    raise SystemExit(main())
