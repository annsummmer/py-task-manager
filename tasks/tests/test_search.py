from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Position, Tag, Task, TaskType


class SearchTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice", password="pass12345"
        )
        get_user_model().objects.create_user(
            username="bob", password="pass12345"
        )
        self.client.force_login(self.user)

    def names(self, url_name, params, context_key, attr="name"):
        response = self.client.get(reverse(url_name), params)
        return [getattr(o, attr) for o in response.context[context_key]]

    def test_search_workers_by_username(self):
        self.assertEqual(
            self.names("tasks:worker-list", {"username": "ALI"},
                       "worker_list", "username"),
            ["alice"],
        )

    def test_empty_worker_search_returns_all(self):
        self.assertEqual(
            self.names("tasks:worker-list", {"username": ""},
                       "worker_list", "username"),
            ["alice", "bob"],
        )

    def test_search_tasks_by_name(self):
        task_type = TaskType.objects.create(name="Bug")
        for name in ("Fix login", "Add logo", "Refactor"):
            Task.objects.create(
                name=name, deadline=date(2030, 1, 1), task_type=task_type
            )
        self.assertEqual(
            sorted(self.names("tasks:task-list", {"name": "LOG"},
                              "task_list")),
            ["Add logo", "Fix login"],
        )

    def test_search_without_results(self):
        self.assertEqual(
            self.names("tasks:task-list", {"name": "zzz"}, "task_list"), []
        )

    def test_search_simple_models(self):
        Position.objects.create(name="Developer")
        Position.objects.create(name="Designer")
        TaskType.objects.create(name="Bug")
        Tag.objects.create(name="python-refactoring")
        self.assertEqual(
            self.names("tasks:position-list", {"name": "dev"},
                       "object_list"),
            ["Developer"],
        )
        self.assertEqual(
            self.names("tasks:task-type-list", {"name": "bug"},
                       "object_list"),
            ["Bug"],
        )
        self.assertEqual(
            self.names("tasks:tag-list", {"name": "refactor"},
                       "object_list"),
            ["python-refactoring"],
        )

    def test_search_form_keeps_value(self):
        response = self.client.get(
            reverse("tasks:worker-list"), {"username": "bo"}
        )
        self.assertEqual(
            response.context["search_form"].initial["username"], "bo"
        )

    def test_pagination_keeps_search_query(self):
        for i in range(7):
            get_user_model().objects.create_user(
                username=f"dev{i}", password="pass12345"
            )
        response = self.client.get(
            reverse("tasks:worker-list"), {"username": "dev"}
        )
        self.assertContains(response, "username=dev&amp;page=2")
