from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from taskApp.models import Task


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=200)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class TaskForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Task
        fields = ['title', 'time', 'date', 'done']


class ImportTasksForm(forms.Form):
    csv_file = forms.FileField(label='Upload CSV3 File')


