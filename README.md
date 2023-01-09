# Simple task manager written in Python

Hey there!

## Basic installation
Run:
`pip install typer rich`
`pip install git+https://github.com/nachoregulardude/simple_task_manager`
And you should be good to go!
To uninstall:
`pip uninstall task_manager`


## Basic Usage
### Adding tasks:
- You can add new tasks by running `task add '{task_description}' '{task_category}'`

###  View tasks:
- You can look at the tasks you've created by running `task show`. This prints out a neatly formatted table with your tasks.

### Mark as completed:
- You can mark a task as completed by running `task done {task_position}`. This will mark the corresponding task as completed.

### Delete tasks:
- You can delete tasks by running `task delete {position}`.  
- Running `task delete 0` deletes all the tasks!

### Updating tasks:
- You can update tasks by running:
	-  `task update {position} {task_desc} {task_category}` 
- Task description must be an empty string if you want to only change the `task_category`. Just provide one argument to update the `task_description`



## Roadmap
Features to add:
- Integrate way to have tasks stored in a remote server. Currently a Sqlite DB file is created at `~/.config/task_tracker`
- Integrate push notifications for reminders.
- 

## How it works?

When you install and run task_manager. It creates a Sqlite DB file at `~/.config/task_tracker`. Every time you interact with the app the DB file is updated.

Contributions are welcome!
