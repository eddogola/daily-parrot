from django.contrib import admin
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail
from django.db import models as dj_models
from tinymce.widgets import TinyMCE

from main import models, forms

class BlogPostsInline(admin.TabularInline):
    model = models.BlogPost
    
class TopicsInline(admin.TabularInline):
    model = models.Topic

class BlogPostsTagsInline(admin.TabularInline):
    model = models.BlogPost.tags.through
    
class ProfileTopicsInline(admin.TabularInline):
    model = models.Profile.topics.through

@admin.register(models.Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline','slug', 'classification','blog_posts', 'topic_banner',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = (
        ProfileTopicsInline,
    )
    
    def blog_posts(self, obj):
        blog_posts_count = obj.blog_posts.count()
        return blog_posts_count
    
    def topic_banner(self, obj):
        banner = get_thumbnail(obj.banner, '152x131')
        return format_html(
            "<img src='{}'>".format(banner.url)
        )
    
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (
        BlogPostsTagsInline,
    )
    
@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title','tagline', 'slug', 'topic', 'author', 'created',
                     'updated', 'active', 'get_banner')
    list_editable = ('active',)
    search_fields = ('title', 'body', 'author',)
    list_filter = ('active', 'created', 'updated',)
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        dj_models.TextField: {'widget': TinyMCE(attrs={'cols':80,'rows':30})}
    }
    inlines = (
        BlogPostsTagsInline,
    )
    
    def get_banner(self, obj):
        banner = get_thumbnail(obj.banner, '152x131')
        return format_html(
            "<img src='{}'>".format(banner.url)
        )

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'avatar_thumbnail',)
    inlines = (
        BlogPostsInline,
        ProfileTopicsInline,
    )

    def get_email(self, obj):
        return obj.user.email
    
    def avatar_thumbnail(self, obj):
        thumbnail = get_thumbnail(obj.avatar, "142x131")
        return format_html(
            '<img src="{}">'.format(thumbnail.url)
        )

@admin.register(models.Classification)
class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (
        TopicsInline,
    )