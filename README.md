# SeniorProject

## Collaborators:
- Nicholas Hotelling
- Lucas Pierce
- Baylor Pond
- Nick Perlich

## Procedure for Contributing:
### When you first clone the repository:
- download mypy extension for vs code
- download flake8 extension for vs code
- pip install black
- pip install isort
### Before writing any code:
- check Trello board for any tasks that need to be started
- create an issue on github for that task
- create a branch from the opened issue
- open your code editor, and only work on this branch
### After writing your code:
- before commiting make sure all flake8 and mypy errors are resolved
- black <filepath> on any files you have changed (it is recursive so it can be called on a directory)
- isort <filepath> on any files you have changed (it is recursive so it can be called on a directory)
- now you can make a commit
- when done making commits, push your code
- then make a pull request and make sure super linter is happy with you
- then you can merge, if everyone else is cool with it