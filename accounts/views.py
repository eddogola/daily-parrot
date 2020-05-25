from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView as BasePasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from main.tokens import account_activation_token
from accounts.forms import UserCreationForm
from main.models import Profile

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('account_activation_sent')
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        user.refresh_from_db()
        Profile.objects.create(user=user)
        
        #send confirmation email
        current_site = get_current_site(self.request)
        subject = 'Activate your Daily Parrot account'
        message = render_to_string('email/account_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
        user.email_user(subject, message)
        messages.success(self.request, 'confirm your email')
        return redirect(self.success_url)
    
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.confirmed = True
        user.save()
        user.profile.save()
        messages.success(request, 'you may now log in.')
        return redirect('login')
    else:
        messages.warning(request, 'invalid account activation token')
        return redirect(reverse('home'))
    
class LoginView(BaseLoginView):
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)

class PasswordResetView(BasePasswordResetView):
    subject_template_name = 'email/password_reset_subject.txt'
    email_template_name = 'email/password_reset.html'
    html_email_template_name = 'email/password_reset.html'
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs) 
    
class PasswordResetConfirmView(BasePasswordResetConfirmView):
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'password reset successful')
        return redirect(self.success_url)
        