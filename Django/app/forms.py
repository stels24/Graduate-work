from django import forms
from app.models import Task, Category


class TaskForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    data_end_plan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    data_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Task
        fields = ['name', 'description', 'category', 'data_end_plan', 'status', 'data_end']