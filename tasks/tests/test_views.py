from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Position, Tag, Task, TaskType


class BaseTestCase(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Bug")
        self.user = get_user_model().objects.create_user(
            username="user", password="pass12345", position=self.position
        )
        self.client.force_login(self.user)

    def make_task(self, name="Task", **kwargs):
        kwargs.setdefault("deadline", date(2030, 1, 1))
        kwargs.setdefault("task_type", self.task_type)
        return Task.objects.create(name=name, **kwargs)


class PrivateAccessTests(TestCase):
    def test_login_required(self):
        urls = [
            reverse("tasks:index"),
            reverse("tasks:task-list"),
            reverse("tasks:worker-list"),
            reverse("tasks:position-list"),
            reverse("tasks:task-type-list"),
            reverse("tasks:tag-list"),
            reverse("tasks:task-create"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn("/accounts/login/", response.url)


class IndexTests(BaseTestCase):
    def test_index_shows_counts_and_my_open_tasks(self):
        mine = self.make_task("Mine")
        mine.assignees.add(self.user)
        self.make_task("Other")
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.context["num_tasks"], 2)
        self.assertEqual(response.context["num_open_tasks"], 2)
        self.assertEqual(list(response.context["my_open_tasks"]), [mine])


class TaskViewsTests(BaseTestCase):
    def test_create_task(self):
        response = self.client.post(
            reverse("tasks:task-create"),
            {
                "name": "New",
                "deadline": "2099-01-01",
                "priority": Task.Priority.URGENT,
                "task_type": self.task_type.pk,
                "assignees": [self.user.pk],
            },
        )
        task = Task.objects.get(name="New")
        self.assertRedirects(response, task.get_absolute_url())
        self.assertEqual(list(task.assignees.all()), [self.user])

    def test_update_task(self):
        task = self.make_task()
        self.client.post(
            reverse("tasks:task-update", args=[task.pk]),
            {
                "name": "Renamed",
                "deadline": "2099-01-01",
                "priority": Task.Priority.LOW,
                "task_type": self.task_type.pk,
            },
        )
        task.refresh_from_db()
        self.assertEqual(task.name, "Renamed")

    def test_delete_task(self):
        task = self.make_task()
        self.client.post(reverse("tasks:task-delete", args=[task.pk]))
        self.assertFalse(Task.objects.exists())

    def test_toggle_completed(self):
        task = self.make_task()
        url = reverse("tasks:toggle-task-completed", args=[task.pk])
        self.client.post(url)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)
        self.client.post(url)
        task.refresh_from_db()
        self.assertFalse(task.is_completed)

    def test_toggle_completed_requires_post(self):
        task = self.make_task()
        self.client.get(reverse("tasks:toggle-task-completed", args=[task.pk]))
        task.refresh_from_db()
        self.assertFalse(task.is_completed)

    def test_toggle_assign(self):
        task = self.make_task()
        url = reverse("tasks:toggle-task-assign", args=[task.pk])
        self.client.post(url)
        self.assertIn(self.user, task.assignees.all())
        self.client.post(url)
        self.assertNotIn(self.user, task.assignees.all())

    def test_toggle_assign_unknown_task_404(self):
        response = self.client.post(
            reverse("tasks:toggle-task-assign", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_status_filter(self):
        self.make_task("open")
        self.make_task("finished", is_completed=True)
        url = reverse("tasks:task-list")
        open_names = [
            t.name for t in self.client.get(url, {"status": "open"})
            .context["task_list"]
        ]
        done_names = [
            t.name for t in self.client.get(url, {"status": "done"})
            .context["task_list"]
        ]
        self.assertEqual(open_names, ["open"])
        self.assertEqual(done_names, ["finished"])

    def test_pagination(self):
        for i in range(7):
            self.make_task(f"task {i}")
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(len(response.context["task_list"]), 5)
        self.assertTrue(response.context["is_paginated"])


class WorkerViewsTests(BaseTestCase):
    def test_detail_splits_open_and_completed(self):
        open_task = self.make_task("open")
        done_task = self.make_task("done", is_completed=True)
        open_task.assignees.add(self.user)
        done_task.assignees.add(self.user)
        response = self.client.get(
            reverse("tasks:worker-detail", args=[self.user.pk])
        )
        self.assertEqual(list(response.context["open_tasks"]), [open_task])
        self.assertEqual(
            list(response.context["completed_tasks"]), [done_task]
        )

    def test_list_counts_tasks(self):
        self.make_task("open").assignees.add(self.user)
        self.make_task("done", is_completed=True).assignees.add(self.user)
        self.make_task("done2", is_completed=True).assignees.add(self.user)
        response = self.client.get(reverse("tasks:worker-list"))
        worker = response.context["worker_list"][0]
        self.assertEqual(worker.open_count, 1)
        self.assertEqual(worker.done_count, 2)

    def test_create_worker(self):
        self.client.post(
            reverse("tasks:worker-create"),
            {
                "username": "created",
                "password1": "Str0ngPass!123",
                "password2": "Str0ngPass!123",
                "first_name": "A",
                "last_name": "B",
                "position": self.position.pk,
            },
        )
        self.assertTrue(
            get_user_model().objects.filter(username="created").exists()
        )

    def test_update_worker_position(self):
        other = Position.objects.create(name="QA")
        self.client.post(
            reverse("tasks:worker-update", args=[self.user.pk]),
            {"first_name": "X", "last_name": "Y", "position": other.pk},
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.position, other)


class SimpleModelViewsTests(BaseTestCase):
    CASES = [
        ("position", Position, "Developer"),
        ("task-type", TaskType, "Bug"),
        ("tag", Tag, "api"),
    ]

    def test_crud(self):
        for prefix, model, _ in self.CASES:
            with self.subTest(prefix):
                self.client.post(
                    reverse(f"tasks:{prefix}-create"), {"name": "brand new"}
                )
                obj = model.objects.get(name="brand new")
                self.client.post(
                    reverse(f"tasks:{prefix}-update", args=[obj.pk]),
                    {"name": "changed"},
                )
                obj.refresh_from_db()
                self.assertEqual(obj.name, "changed")
                response = self.client.get(reverse(f"tasks:{prefix}-list"))
                self.assertEqual(response.status_code, 200)
                self.client.post(
                    reverse(f"tasks:{prefix}-delete", args=[obj.pk])
                )
                self.assertFalse(model.objects.filter(pk=obj.pk).exists())

    def test_deleting_position_keeps_worker(self):
        self.client.post(
            reverse("tasks:position-delete", args=[self.position.pk])
        )
        self.user.refresh_from_db()
        self.assertIsNone(self.user.position)
