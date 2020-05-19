from django import forms
from tinymce.widgets import TinyMCE

from main import models

class BlogPostForm(forms.ModelForm):
    
    body = forms.CharField(widget=TinyMCE(attrs={'cols':80,'rows':30}))
    
    class Meta:
        model = models.BlogPost
        exclude = []
        
class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    avatar = forms.ImageField()
    bio = forms.CharField()