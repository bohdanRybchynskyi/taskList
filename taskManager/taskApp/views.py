import codecs
import csv
import logging

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import FormView

from .forms import LoginForm, RegisterForm, TaskForm, ImportTasksForm
from django.views.generic import ListView

from .kafka_producer import KafkaMessageProducer
from .models import Task


logging.basicConfig(filename='app.log', level=logging.ERROR)


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect('task_list')
        else:
            messages.error(self.request, 'Invalid username or password.')
            return super().form_invalid(form)


class RegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()
        return redirect('login')


class TaskListView(ListView):
    model = Task
    template_name = 'task/tasks.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)

        filter_date = self.request.GET.get('date', None)

        if filter_date:
            queryset = queryset.filter(date=filter_date)

        return queryset


def create_task(request):
    form = TaskForm()
    import_form = ImportTasksForm()

    if request.method == 'POST':
        if 'create_task' in request.POST:
            form = TaskForm(request.POST)
            if form.is_valid():
                form.instance.user = request.user
                form.save()

                message = {
                    'datetime': datetime.now().isoformat(),
                    'title': form.instance.title,
                    'user': request.user.username,
                    'operation': "Create task"
                }
                send_message("task_created", message)

                return redirect('task_list')
        else:
            import_form = ImportTasksForm(request.POST, request.FILES)
            if import_form.is_valid():
                csv_file = import_form.cleaned_data['csv_file']

                with csv_file.open('r') as file:
                    csvreader = csv.reader(codecs.iterdecode(file, 'utf-8'))
                    for row in csvreader:
                        Task.objects.create(title=row[0], time=row[1], date=row[2], done=row[3], user=request.user)
                        message = {
                            'datetime': datetime.now().isoformat(),
                            'title': form.instance.title,
                            'user': request.user.username,
                            'operation': "Create task"
                        }
                        send_message('created_task', message)

                return redirect('task_list')

    return render(request, 'task/create_task.html', {'form': form, 'import_form': import_form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()

            message = {
                'datetime': datetime.now().isoformat(),
                'title': form.instance.title,
                'user': request.user.username,
                'operation': "Update task"
            }
            send_message('task_updated', message)

            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task/edit_task.html', {'form': form})


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        title = task.title
        task.delete()

        message = {
            'datetime': datetime.now().isoformat(),
            'title': title,
            'user': request.user.username,
            'operation': "Delete task"
        }
        send_message('task_deleted', message)

        return redirect('task_list')


def toggle_task_done(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.done = not task.done

    if task.done:
        message = {
            'datetime': datetime.now().isoformat(),
            'title': task.title,
            'user': request.user.username,
            'operation': "Task completed"
        }
        send_message('task_completed', message)
    else:
        message = {
            'datetime': datetime.now().isoformat(),
            'title': task.title,
            'user': request.user.username,
            'operation': "Update task"
        }
        send_message('task_updated', message)
    task.save()
    return HttpResponse()


def home(request):
    return render(request, 'home/index.html')


def send_message(topic, message):
    try:
        producer = KafkaMessageProducer(topic)
        producer.send_message(message)
        producer.close()
    except Exception as e:
        logging.error("Error during the task creation: %s", e)
        return HttpResponseServerError()
