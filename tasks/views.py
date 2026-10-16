from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from .forms import (
    NameSearchForm,
    TaskForm,
    TaskSearchForm,
    WorkerCreationForm,
    WorkerPositionUpdateForm,
    WorkerSearchForm,
)
from .models import Position, Tag, Task, TaskType, Worker


@login_required
def index(request):
    """Home page: overall numbers and the current user's open tasks."""
    my_open_tasks = (
        Task.objects.filter(assignees=request.user, is_completed=False)
        .select_related("task_type")
        .order_by("deadline")
    )
    context = {
        "num_tasks": Task.objects.count(),
        "num_open_tasks": Task.objects.filter(is_completed=False).count(),
        "num_workers": Worker.objects.count(),
        "my_open_tasks": my_open_tasks,
    }
    return render(request, "tasks/index.html", context=context)


class SearchMixin:
    """Filter the queryset with `search_field__icontains` from GET params."""

    search_field = "name"
    search_form_class = NameSearchForm
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        value = self.request.GET.get(self.search_field, "")
        context["search_form"] = self.search_form_class(
            initial={self.search_field: value}
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        value = self.request.GET.get(self.search_field)
        if value:
            queryset = queryset.filter(
                **{f"{self.search_field}__icontains": value}
            )
        return queryset


# Position / TaskType / Tag share the same simple templates.
class SimpleListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    template_name = "tasks/simple_list.html"
    context_object_name = "object_list"
    entity = ""
    url_prefix = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity"] = self.entity
        context["url_prefix"] = self.url_prefix
        return context


class SimpleFormMixin(LoginRequiredMixin):
    template_name = "tasks/simple_form.html"
    fields = "__all__"
    entity = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity"] = self.entity
        return context


class SimpleDeleteMixin(LoginRequiredMixin):
    template_name = "tasks/simple_confirm_delete.html"
    entity = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity"] = self.entity
        return context


class PositionListView(SimpleListView):
    model = Position
    entity = "position"
    url_prefix = "position"


class PositionCreateView(SimpleFormMixin, generic.CreateView):
    model = Position
    entity = "position"
    success_url = reverse_lazy("tasks:position-list")


class PositionUpdateView(SimpleFormMixin, generic.UpdateView):
    model = Position
    entity = "position"
    success_url = reverse_lazy("tasks:position-list")


class PositionDeleteView(SimpleDeleteMixin, generic.DeleteView):
    model = Position
    entity = "position"
    success_url = reverse_lazy("tasks:position-list")


class TaskTypeListView(SimpleListView):
    model = TaskType
    entity = "task type"
    url_prefix = "task-type"


class TaskTypeCreateView(SimpleFormMixin, generic.CreateView):
    model = TaskType
    entity = "task type"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeUpdateView(SimpleFormMixin, generic.UpdateView):
    model = TaskType
    entity = "task type"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeDeleteView(SimpleDeleteMixin, generic.DeleteView):
    model = TaskType
    entity = "task type"
    success_url = reverse_lazy("tasks:task-type-list")


class TagListView(SimpleListView):
    model = Tag
    entity = "tag"
    url_prefix = "tag"


class TagCreateView(SimpleFormMixin, generic.CreateView):
    model = Tag
    entity = "tag"
    success_url = reverse_lazy("tasks:tag-list")


class TagUpdateView(SimpleFormMixin, generic.UpdateView):
    model = Tag
    entity = "tag"
    success_url = reverse_lazy("tasks:tag-list")


class TagDeleteView(SimpleDeleteMixin, generic.DeleteView):
    model = Tag
    entity = "tag"
    success_url = reverse_lazy("tasks:tag-list")


class TaskListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Task
    search_form_class = TaskSearchForm

    def get_queryset(self):
        queryset = super().get_queryset().select_related("task_type")
        queryset = queryset.prefetch_related("assignees", "tags")
        status = self.request.GET.get("status")
        if status == "open":
            queryset = queryset.filter(is_completed=False)
        elif status == "done":
            queryset = queryset.filter(is_completed=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "")
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.select_related("task_type").prefetch_related(
        "assignees", "tags"
    )


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_initial(self):
        return {"assignees": [self.request.user]}


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:task-list")


@login_required
def toggle_task_completed(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])
    return HttpResponseRedirect(reverse("tasks:task-detail", args=[pk]))


@login_required
def toggle_assign_to_task(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        if task.assignees.filter(pk=request.user.pk).exists():
            task.assignees.remove(request.user)
        else:
            task.assignees.add(request.user)
    return HttpResponseRedirect(reverse("tasks:task-detail", args=[pk]))


class WorkerListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Worker
    search_field = "username"
    search_form_class = WorkerSearchForm

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("position")
            .annotate(
                open_count=Count(
                    "tasks", filter=Q(tasks__is_completed=False)
                ),
                done_count=Count(
                    "tasks", filter=Q(tasks__is_completed=True)
                ),
            )
        )


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = Worker.objects.select_related("position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = self.object.tasks.select_related("task_type")
        context["open_tasks"] = tasks.filter(is_completed=False)
        context["completed_tasks"] = tasks.filter(is_completed=True)
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerPositionUpdateForm


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("tasks:worker-list")
