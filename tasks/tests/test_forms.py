from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from tasks.forms import TaskForm, WorkerCreationForm
from tasks.models import Position, Task, TaskType


class TaskFormTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")

    def form_data(self, deadline):
        return {
            "name": "Fix",
            "deadline": deadline,
            "priority": Task.Priority.HIGH,
            "task_type": self.task_type.pk,
        }

    def test_future_deadline_is_valid(self):
        deadline = timezone.localdate() + timedelta(days=1)
        self.assertTrue(TaskForm(data=self.form_data(deadline)).is_valid())

    def test_past_deadline_is_invalid(self):
        deadline = timezone.localdate() - timedelta(days=1)
        form = TaskForm(data=self.form_data(deadline))
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)

    def test_unchanged_past_deadline_allowed_on_update(self):
        deadline = timezone.localdate() - timedelta(days=5)
        task = Task.objects.create(
            name="Old", deadline=deadline, task_type=self.task_type
        )
        data = self.form_data(deadline)
        data["is_completed"] = True
        self.assertTrue(TaskForm(data=data, instance=task).is_valid())


class WorkerCreationFormTests(TestCase):
    def test_creation_with_position(self):
        position = Position.objects.create(name="QA")
        form = WorkerCreationForm(
            data={
                "username": "new_worker",
                "password1": "Str0ngPass!123",
                "password2": "Str0ngPass!123",
                "first_name": "New",
                "last_name": "Worker",
                "email": "new@example.com",
                "position": position.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().position, position)
