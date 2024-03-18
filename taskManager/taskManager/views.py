from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.generic import FormView
from .forms import LoginForm, RegisterForm

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
