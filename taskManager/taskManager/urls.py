from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from taskApp.views import LoginView, RegisterView, TaskListView, create_task, edit_task, delete_task, toggle_task_done, \
    home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', login_required(LogoutView.as_view()), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('task/list/', login_required(TaskListView.as_view()), name='task_list'),
    path('task/create/', login_required(create_task), name='create_task'),
    path('task/edit/<int:task_id>/', login_required(edit_task), name='edit_task'),
    path('task/delete/<int:task_id>/', login_required(delete_task), name='delete_task'),
    path('task/done/<int:task_id>/', login_required(toggle_task_done), name='toggle_task_done'),
]
