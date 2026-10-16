from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from tasks.models import Position


class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            username="admin", password="pass12345"
        )
        self.client.force_login(self.admin)
        self.position = Position.objects.create(name="QA")
        self.worker = get_user_model().objects.create_user(
            username="w", password="pass12345", position=self.position
        )

    def test_worker_position_in_list(self):
        response = self.client.get(reverse("admin:tasks_worker_changelist"))
        self.assertContains(response, "QA")

    def test_worker_position_on_change_page(self):
        url = reverse("admin:tasks_worker_change", args=[self.worker.pk])
        self.assertContains(self.client.get(url), "Additional info")

    def test_worker_position_on_add_page(self):
        response = self.client.get(reverse("admin:tasks_worker_add"))
        self.assertContains(response, "position")
