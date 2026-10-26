# IT Company Task Manager
> A Django task manager for IT teams: create, assign and complete tasks before their deadlines.

A Django task manager for an IT team (developers, designers, project managers, QA).
Everyone can create a task, assign it to team members and mark it as done before the deadline.

## Live demo

- Deployed app: https://py-task-manager-z1c3.onrender.com/

Test user (regular account, not an admin): `dev1` / `password12345`

## Installing / Getting started

Requires Python 3 and pip.

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata task_manager_db_data.json   # optional demo data
python manage.py runserver
```

The app is then available at http://127.0.0.1:8000/.

Demo users (from the fixture): `dev1`, `qa1`, `des1`, `ops1` / `password12345`.

### Initial Configuration

Create a `.env` file in the project root (see [Configuration](#configuration)) before running the app:

```shell
SECRET_KEY=your-secret-key
DEBUG=True
```

## Developing

```shell
git clone https://github.com/annsummmer/py-task-manager.git
cd py-task-manager/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### Checks

```shell
flake8
python manage.py test
```

## Data model

- **Position** (Developer, QA, Designer, ...) 1 — n **Worker** (`AbstractUser` + `position`)
- **TaskType** (Bug, New feature, Refactoring, ...) 1 — n **Task**
- **Task**: `name`, `description`, `deadline`, `is_completed`, `priority` (Urgent/High/Medium/Low),
  `task_type`, `assignees` (m2m Worker), `tags` (m2m Tag)
- **Tag** (e.g. `landing-page-layout`) m — n **Task**

## Features

- Login-protected CRUD for tasks, workers, positions, task types and tags
- Search: tasks by name, workers by username, positions / task types / tags by name
  (search is kept while paginating); tasks can also be filtered by completed / not completed
- "Mark as done" and "Assign me / Unassign me" buttons on the task page (POST only)
- Worker page shows completed and not completed tasks separately; worker list shows the counts
- Home page lists the current user's open tasks

## Configuration

Settings are read from environment variables, or from the `.env` file in the project root.

#### SECRET_KEY
Type: `String`  
Default: none (required)

Django secret key. Use a long random value and keep it out of version control.

#### DEBUG
Type: `Boolean`  
Default: none (required)

Enables Django debug mode. Set it to `False` in production.

## Contributing

Contributions are welcome. Fork the repository, create a feature branch and open a pull request.
Please run `flake8` and `python manage.py test` before submitting.

## Links

- Repository: https://github.com/annsummmer/py-task-manager
- Issue tracker: https://github.com/annsummmer/py-task-manager/issues

## Licensing

No license has been chosen for this project yet.
