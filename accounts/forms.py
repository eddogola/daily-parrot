from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth import get_user_model

class UserCreationForm(BaseUserCreationForm):
    
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username','email',
                   'password1', 'password2')
        