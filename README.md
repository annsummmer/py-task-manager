# IT Company Task Manager

A Django task manager for an IT team (developers, designers, project managers, QA).
Everyone can create a task, assign it to team members and mark it as done before the deadline.

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

## Run

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata task_manager_db_data.json   # optional demo data
python manage.py runserver
```

Demo users (from the fixture): `admin` / `admin12345`, `dev1`, `qa1`, `des1`, `ops1` / `password12345`.

## Checks

```shell
flake8
python manage.py test
```
# py-task-manager
