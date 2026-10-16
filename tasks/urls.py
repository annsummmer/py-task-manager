from django.urls import path

from . import views

app_name = "tasks"


def crud(prefix, name, list_view, create_view, update_view, delete_view):
    return [
        path(f"{prefix}/", list_view.as_view(), name=f"{name}-list"),
        path(
            f"{prefix}/create/", create_view.as_view(), name=f"{name}-create"
        ),
        path(
            f"{prefix}/<int:pk>/update/",
            update_view.as_view(),
            name=f"{name}-update",
        ),
        path(
            f"{prefix}/<int:pk>/delete/",
            delete_view.as_view(),
            name=f"{name}-delete",
        ),
    ]


urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path(
        "tasks/create/", views.TaskCreateView.as_view(), name="task-create"
    ),
    path(
        "tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"
    ),
    path(
        "tasks/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="task-delete",
    ),
    path(
        "tasks/<int:pk>/toggle-completed/",
        views.toggle_task_completed,
        name="toggle-task-completed",
    ),
    path(
        "tasks/<int:pk>/toggle-assign/",
        views.toggle_assign_to_task,
        name="toggle-task-assign",
    ),
    path("workers/", views.WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/create/",
        views.WorkerCreateView.as_view(),
        name="worker-create",
    ),
    path(
        "workers/<int:pk>/",
        views.WorkerDetailView.as_view(),
        name="worker-detail",
    ),
    path(
        "workers/<int:pk>/update/",
        views.WorkerUpdateView.as_view(),
        name="worker-update",
    ),
    path(
        "workers/<int:pk>/delete/",
        views.WorkerDeleteView.as_view(),
        name="worker-delete",
    ),
]
urlpatterns += crud(
    "positions", "position", views.PositionListView,
    views.PositionCreateView, views.PositionUpdateView,
    views.PositionDeleteView,
)
urlpatterns += crud(
    "task-types", "task-type", views.TaskTypeListView,
    views.TaskTypeCreateView, views.TaskTypeUpdateView,
    views.TaskTypeDeleteView,
)
urlpatterns += crud(
    "tags", "tag", views.TagListView, views.TagCreateView,
    views.TagUpdateView, views.TagDeleteView,
)
