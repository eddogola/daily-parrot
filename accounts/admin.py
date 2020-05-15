from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import Profile
from main.models import BlogPost

@admin.register(get_user_model())
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal Information',
            {
                'fields': ('first_name', 'last_name')
            }
        ),
        (
            'Permissions',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 
                           'groups', 'user_permissions')
            }
        ),
        (
            'Important dates',
            {
                'fields': ('last_login', 'date_joined',)
            }
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes':('wide',),
                'fields': ('email', 'password1', 'password2'),
            }
        ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class BlogPostsInline(admin.TabularInline):
    model = BlogPost

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_avatar',)
    inlines = (
        BlogPostsInline,
    )

    def get_email(self, obj):
        return obj.user.email
    
    def get_avatar(self, obj):
        return format_html(
            '<img src="{}">'.format(obj.avatar.url)
        )
