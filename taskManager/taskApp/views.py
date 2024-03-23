import codecs
import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import FormView
from .forms import LoginForm, RegisterForm, TaskForm, ImportTasksForm
from django.views.generic import ListView

from .kafka_producer import KafkaMessageProducer
from .models import Task


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'You have been successfully logged in.')
            return redirect('/')
        else:
            messages.error(self.request, 'Invalid username or password.')
            return super().form_invalid(form)


class RegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your account has been successfully created.')
        return redirect('/')


class TaskListView(ListView):
    model = Task
    template_name = 'task/tasks.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


def create_task(request):
    form = TaskForm()
    import_form = ImportTasksForm()

    if request.method == 'POST':
        if 'create_task' in request.POST:
            messages.warning(request, 'No tasks were imported.')
            form = TaskForm(request.POST)
            if form.is_valid():
                form.instance.user = request.user
                form.save()

                kafka_broker = 'kafka:9092'
                topic = 'task_created'
                producer = KafkaMessageProducer(kafka_broker, topic)

                message = {
                    'datetime': datetime.now().isoformat(),
                    'title': form.instance.title,
                    'user': request.user.username,
                    'operation': topic
                }
                producer.send_message(message)

                producer.close()

                return redirect('task-list')
        else:
            import_form = ImportTasksForm(request.POST, request.FILES)
            if import_form.is_valid():
                csv_file = import_form.cleaned_data['csv_file']

                with csv_file.open('r') as file:
                    csvreader = csv.reader(codecs.iterdecode(file, 'utf-8'))
                    for row in csvreader:
                        Task.objects.create(title=row[0], time=row[1], date=row[2], done=row[3], user=request.user)

                return redirect('task-list')

    return render(request, 'task/create_task.html', {'form': form, 'import_form': import_form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()

            kafka_broker = 'kafka:9092'
            topic = 'task_updated'
            producer = KafkaMessageProducer(kafka_broker, topic)

            message = {
                'datetime': datetime.now().isoformat(),
                'title': form.instance.title,
                'user': request.user.username,
                'operation': topic
            }
            producer.send_message(message)

            producer.close()

            return redirect('task-list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task/edit_task.html', {'form': form})


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        task.delete()

        kafka_broker = 'kafka:9092'
        topic = 'task_deleted'
        producer = KafkaMessageProducer(kafka_broker, topic)

        message = {
            'datetime': datetime.now().isoformat(),
            'title': 'task is deleted',
            'user': request.user.username,
            'operation': topic
        }
        producer.send_message(message)

        producer.close()

        return redirect('task-list')


def toggle_task_done(task_id):
    task = get_object_or_404(Task, id=task_id)
    task.done = not task.done
    task.save()
    return HttpResponse()
