from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from tasks.models import Position, Tag, Task, TaskType


class ModelsTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Bug")
        self.worker = get_user_model().objects.create_user(
            username="john",
            password="pass12345",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )

    def test_position_str(self):
        self.assertEqual(str(self.position), "Developer")

    def test_task_type_str(self):
        self.assertEqual(str(self.task_type), "Bug")

    def test_tag_str(self):
        self.assertEqual(str(Tag.objects.create(name="api")), "api")

    def test_worker_str(self):
        self.assertEqual(str(self.worker), "john (John Doe)")

    def test_worker_absolute_url(self):
        self.assertEqual(
            self.worker.get_absolute_url(), f"/workers/{self.worker.pk}/"
        )

    def test_worker_position(self):
        self.assertEqual(self.worker.position, self.position)

    def test_task_defaults(self):
        task = Task.objects.create(
            name="Fix", deadline=date(2030, 1, 1), task_type=self.task_type
        )
        self.assertFalse(task.is_completed)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertEqual(str(task), "Fix")

    def test_task_many_to_many(self):
        task = Task.objects.create(
            name="Fix", deadline=date(2030, 1, 1), task_type=self.task_type
        )
        tag = Tag.objects.create(name="api")
        task.assignees.add(self.worker)
        task.tags.add(tag)
        self.assertIn(task, self.worker.tasks.all())
        self.assertIn(task, tag.tasks.all())

    def test_tasks_ordered_open_first_then_deadline(self):
        done = Task.objects.create(
            name="done", deadline=date(2030, 1, 1),
            task_type=self.task_type, is_completed=True,
        )
        late = Task.objects.create(
            name="late", deadline=date(2030, 3, 1), task_type=self.task_type
        )
        soon = Task.objects.create(
            name="soon", deadline=date(2030, 2, 1), task_type=self.task_type
        )
        self.assertEqual(list(Task.objects.all()), [soon, late, done])
