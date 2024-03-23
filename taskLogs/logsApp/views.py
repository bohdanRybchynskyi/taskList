from django.shortcuts import render

from .models import LogEntry


def index(request):
    logs = LogEntry.objects.all()
    return render(request, 'index.html', {'logs': logs})


def filter_logs(request):
    user = request.GET.get('user')
    if user:
        logs = LogEntry.objects.filter(user__icontains=user)
    else:
        logs = LogEntry.objects.all()
    return render(request, 'index.html', {'logs': logs})