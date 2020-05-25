from django.views.generic import TemplateView
from django.urls import path

from accounts import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('account_activation_sent', TemplateView.as_view(template_name='account_activation_sent.html'), 
         name='account_activation_sent'),
]