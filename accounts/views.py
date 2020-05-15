from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView as BasePasswordResetConfirmView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from accounts.forms import UserCreationForm
from main.models import Profile

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        messages.success(self.request, 'you may now sign up.')
        return redirect(self.success_url)
    
class LoginView(BaseLoginView):
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)
    
class PasswordResetView(BasePasswordResetView):
    subject_template_name = 'email/password_reset_subject.txt'
    email_template_name = 'email/password_reset.html'
    html_email_template_name = 'email/password_reset.html'
    
class PasswordResetConfirmView(BasePasswordResetConfirmView):
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'password reset successful')
        return redirect(self.success_url)
        