from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Tag, Task, Worker


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "is_completed",
            "assignees",
            "tags",
        ]

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        # only new tasks (or changed deadlines) must lie in the future
        if "deadline" in self.changed_data:
            if deadline < timezone.localdate():
                raise forms.ValidationError("Deadline cannot be in the past")
        return deadline


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "position",
        )


class WorkerPositionUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["first_name", "last_name", "email", "position"]


def search_form(field_name, placeholder):
    """Build a single-field GET search form."""
    return type(
        f"{field_name.capitalize()}SearchForm",
        (forms.Form,),
        {
            field_name: forms.CharField(
                max_length=255,
                required=False,
                label="",
                widget=forms.TextInput(attrs={"placeholder": placeholder}),
            )
        },
    )


TaskSearchForm = search_form("name", "Search by task name")
WorkerSearchForm = search_form("username", "Search by username")
NameSearchForm = search_form("name", "Search by name")
